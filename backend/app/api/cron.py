"""Scheduled-task (Cron) API – reads from Hermes cron jobs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import subprocess
import json
import os
import sys

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.cron_execution import CronExecution, ExecutionStatus

router = APIRouter(prefix="/api/cron", tags=["定时任务"])


def get_hermes_cron_jobs() -> list[dict]:
    """从 Hermes 获取定时任务列表."""
    try:
        # 使用 Python 脚本调用 cronjob 工具
        script = '''
import sys
import json
sys.path.insert(0, 'G:/g/Hermes/hermes-agent')
from tools.cronjob_tools import cronjob

result = cronjob(action='list', include_disabled=True)
print(result)
'''
        
        result = subprocess.run(
            ["python", "-c", script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                if isinstance(data, dict) and 'jobs' in data:
                    jobs = data['jobs']
                    formatted_jobs = []
                    for job in jobs:
                        formatted_jobs.append({
                            'id': job.get('job_id', ''),
                            'name': job.get('name', ''),
                            'schedule': job.get('schedule', ''),
                            'enabled': job.get('enabled', True),
                            'last_run': job.get('last_run_at'),
                            'status': job.get('last_status'),
                        })
                    return formatted_jobs
            except json.JSONDecodeError:
                pass
        
        return []
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
        result = subprocess.run(
            ["hermes", "cron", "run", job_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        execution = CronExecution(
            cron_job_id=job_id,
            status=ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
            result=result.stdout if result.returncode == 0 else None,
            error_message=result.stderr if result.returncode != 0 else None,
        )
        db.add(execution)
        db.commit()
        
        if result.returncode == 0:
            return {"success": True, "message": "任务已触发执行"}
        else:
            return {"success": False, "message": f"执行失败: {result.stderr}"}
    except Exception as e:
        return {"success": False, "message": f"执行失败: {e}"}
