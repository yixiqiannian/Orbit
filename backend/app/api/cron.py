"""Scheduled-task (Cron) API – proxies to Hermes Cron and records executions."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.cron_execution import CronExecution, ExecutionStatus
from app.schemas.cron import CronJobResponse, CronExecutionResponse, CronRunResponse

router = APIRouter(prefix="/api/cron", tags=["定时任务"])


def is_hermes_configured() -> bool:
    """Check if Hermes API is configured."""
    return bool(settings.HERMES_API_URL and settings.HERMES_API_KEY)


@router.get("/jobs", response_model=list[CronJobResponse])
async def list_jobs(current_user: User = Depends(get_current_user)):
    """Fetch all cron jobs from Hermes."""
    if not is_hermes_configured():
        return []
    try:
        from app.services.hermes_client import hermes_client
        jobs = await hermes_client.list_jobs()
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {e}")


@router.get("/jobs/{job_id}", response_model=CronJobResponse)
async def get_job(job_id: str, current_user: User = Depends(get_current_user)):
    """Fetch a single cron job from Hermes."""
    if not is_hermes_configured():
        raise HTTPException(status_code=400, detail="Hermes API 未配置")
    try:
        from app.services.hermes_client import hermes_client
        job = await hermes_client.get_job(job_id)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务详情失败: {e}")


@router.post("/jobs/{job_id}/run", response_model=CronRunResponse)
async def run_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Trigger a cron job execution and record it in the database."""
    if not is_hermes_configured():
        return CronRunResponse(success=False, message="Hermes API 未配置，请在 .env 中设置 HERMES_API_URL 和 HERMES_API_KEY")
    try:
        from app.services.hermes_client import hermes_client
        result = await hermes_client.run_job(job_id)
        execution = CronExecution(
            cron_job_id=job_id,
            status=ExecutionStatus.SUCCESS,
            result=str(result),
        )
        db.add(execution)
        db.commit()
        return CronRunResponse(success=True, message="任务已触发执行")
    except Exception as e:
        execution = CronExecution(
            cron_job_id=job_id,
            status=ExecutionStatus.FAILED,
            error_message=str(e),
        )
        db.add(execution)
        db.commit()
        return CronRunResponse(success=False, message=f"执行失败: {e}")


@router.get("/executions", response_model=list[CronExecutionResponse])
def list_executions(
    job_id: str = Query(None, description="按任务 ID 过滤"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent cron execution records, optionally filtered by job ID."""
    query = db.query(CronExecution)
    if job_id:
        query = query.filter(CronExecution.cron_job_id == job_id)
    return query.order_by(CronExecution.executed_at.desc()).limit(50).all()


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str, current_user: User = Depends(get_current_user)):
    """Pause a cron job via Hermes."""
    if not is_hermes_configured():
        return {"success": False, "message": "Hermes API 未配置"}
    try:
        from app.services.hermes_client import hermes_client
        await hermes_client.pause_job(job_id)
        return {"success": True, "message": "任务已暂停"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"暂停失败: {e}")


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str, current_user: User = Depends(get_current_user)):
    """Resume a paused cron job via Hermes."""
    if not is_hermes_configured():
        return {"success": False, "message": "Hermes API 未配置"}
    try:
        from app.services.hermes_client import hermes_client
        await hermes_client.resume_job(job_id)
        return {"success": True, "message": "任务已恢复"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"恢复失败: {e}")
