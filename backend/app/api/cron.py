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

# 设置正确的 HERMES_HOME 路径（必须在导入 cron 模块之前）
# 使用 Windows 格式路径，避免 MSYS2 路径解析问题
os.environ['HERMES_HOME'] = 'G:\\Hermes'

# 添加 hermes-agent 到 Python 路径
if 'G:\\Hermes\\hermes-agent' not in sys.path:
    sys.path.insert(0, 'G:\\Hermes\\hermes-agent')


def get_hermes_cron_jobs() -> list[dict]:
    """从 Hermes 获取定时任务列表."""
    try:
        # 直接读取 jobs.json 文件
        jobs_file = 'G:/Hermes/cron/jobs.json'
        
        if not os.path.exists(jobs_file):
            # 尝试其他路径
            alt_paths = [
                'G:/g/Hermes/cron/jobs.json',
                'C:/Users/Admin/.hermes/cron/jobs.json',
            ]
            for alt_path in alt_paths:
                if os.path.exists(alt_path):
                    jobs_file = alt_path
                    break
        
        if not os.path.exists(jobs_file):
            print(f"Jobs file not found: {jobs_file}")
            return []
        
        with open(jobs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            jobs = data.get('jobs', [])
        
        # 格式化任务数据
        formatted_jobs = []
        for job in jobs:
            schedule = job.get('schedule', {})
            if isinstance(schedule, dict):
                schedule_display = schedule.get('display', '')
            else:
                schedule_display = str(schedule)
            
            formatted_jobs.append({
                'id': job.get('id', ''),
                'name': job.get('name', ''),
                'schedule': schedule_display,
                'enabled': job.get('enabled', True),
                'last_run': job.get('last_run_at'),
                'status': job.get('last_status'),
            })
        
        return formatted_jobs
    except Exception as e:
        print(f"Error getting cron jobs: {e}")
        import traceback
        traceback.print_exc()
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
        env['HERMES_HOME'] = 'G:\\Hermes'
        
        result = subprocess.run(
            ["hermes", "cron", "run", job_id],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
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
