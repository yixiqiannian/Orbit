"""Dashboard aggregation schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.models.task import TaskType, TaskStatus
from app.models.cron_execution import ExecutionStatus


class TaskSummary(BaseModel):
    total: int
    pending: int
    in_progress: int
    completed_today: int
    overdue: int


class CronSummary(BaseModel):
    total_jobs: int
    enabled: int
    recent_executions: int
    success_rate: float


class ReadingSummary(BaseModel):
    total_books: int
    reading: int
    finished: int
    avg_progress: float


class RecentTask(BaseModel):
    id: int
    title: str
    type: TaskType
    status: TaskStatus
    priority: int
    due_date: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class RecentExecution(BaseModel):
    id: int
    cron_job_id: str
    cron_job_name: Optional[str] = None
    status: ExecutionStatus
    executed_at: datetime

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    tasks: TaskSummary
    cron: CronSummary
    reading: ReadingSummary
    recent_tasks: list[RecentTask]
    recent_executions: list[RecentExecution]


class HeatmapResponse(BaseModel):
    start_date: str
    end_date: str
    data: dict[str, int]
