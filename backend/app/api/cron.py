"""Scheduled-task (Cron) API – reads from Hermes cron jobs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import subprocess
import json
import os
import re

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.cron_execution import CronExecution, ExecutionStatus

router = APIRouter(prefix="/api/cron", tags=["定时任务"])

# 正确的 HERMES_HOME 路径
HERMES_HOME = 'G:/g/Hermes'


def get_hermes_cron_jobs() -> list[dict]:
    """从 Hermes 获取定时任务列表."""
    try:
        env = os.environ.copy()
        env['HERMES_HOME'] = HERMES_HOME
        
        result = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        
        if result.returncode != 0:
            return []
        
        if 'No scheduled jobs' in result.stdout:
            return []
        
        jobs = []
        lines = result.stdout.strip().split('\n')
        current_job = {}
        
        for line in lines:
            line = line.strip()
            
            id_match = re.match(r'^([a-f0-9]+)\s+\[(\w+)\]', line)
            if id_match:
                if current_job and 'id' in current_job:
                    jobs.append(current_job)
                current_job = {
                    'id': id_match.group(1),
                    'enabled': id_match.group(2) == 'active',
                    'schedule': '',
                    'name': '',
                    'last_run': None,
                    'status': None,
                }
                continue
            
            if current_job:
                if line.startswith('Name:'):
                    current_job['name'] = line.split(':', 1)[1].strip()
                elif line.startswith('Schedule:'):
                    current_job['schedule'] = line.split(':', 1)[1].strip()
                elif line.startswith('Last run:'):
                    last_run_str = line.split(':', 1)[1].strip()
                    if 'error' in last_run_str.lower():
                        current_job['status'] = 'error'
                        current_job['last_run'] = last_run_str.split('error')[0].strip()
                    elif last_run_str:
                        current_job['status'] = 'ok'
                        current_job['last_run'] = last_run_str
        
        if current_job and 'id' in current_job:
            jobs.append(current_job)
        
        return jobs
    except Exception as e:
        print(f"Error getting cron jobs: {e}")
        return []


@router.get("/jobs/list")
def list_jobs_api(current_user: User = Depends(get_current_user)):
    """获取定时任务列表."""
    jobs = get_hermes_cron_jobs()
    return jobs


@router.get("/executions")
def list_executions(
    job_id: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取执行记录."""
    query = db.query(CronExecution)
    if job_id:
        query = query.filter(CronExecution.cron_job_id == job_id)
    return query.order_by(CronExecution.executed_at.desc()).limit(50).all()


@router.post("/jobs/{job_id}/run")
async def run_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """执行定时任务."""
    try:
        env = os.environ.copy()
        env['HERMES_HOME'] = HERMES_HOME
        
        result = subprocess.run(
            ["hermes", "cron", "run", job_id],
            capture_output=True,
            text=True,
            timeout=120,  # 增加到120秒
            env=env
        )
        
        # 解析输出判断是否成功
        output = result.stdout + result.stderr
        is_success = 'succeeded' in output.lower() or result.returncode == 0
        
        execution = CronExecution(
            cron_job_id=job_id,
            status=ExecutionStatus.SUCCESS if is_success else ExecutionStatus.FAILED,
            result=result.stdout if result.stdout else None,
            error_message=result.stderr if result.stderr else None,
        )
        db.add(execution)
        db.commit()
        
        if is_success:
            return {"success": True, "message": "任务已触发执行", "output": result.stdout}
        else:
            return {"success": False, "message": f"执行失败", "output": result.stdout + result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "message": "执行超时（120秒）"}
    except Exception as e:
        return {"success": False, "message": f"执行失败: {e}"}
