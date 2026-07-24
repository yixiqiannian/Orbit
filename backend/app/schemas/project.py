"""Project schemas."""

from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    status: str
    start_date: Optional[date]
    end_date: Optional[date]
    task_count: int = 0  # 关联任务数量
    completed_count: int = 0  # 已完成任务数量
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
