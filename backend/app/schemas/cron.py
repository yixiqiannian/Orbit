"""Pydantic schemas for the Cron / Scheduled-task endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CronJobResponse(BaseModel):
    id: str
    name: str
    schedule: str
    enabled: bool
    last_run: Optional[datetime] = None
    last_status: Optional[str] = None
    next_run: Optional[datetime] = None


class CronExecutionResponse(BaseModel):
    id: int
    cron_job_id: str
    cron_job_name: Optional[str] = None
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
    executed_at: datetime

    class Config:
        from_attributes = True


class CronRunResponse(BaseModel):
    success: bool
    message: str
