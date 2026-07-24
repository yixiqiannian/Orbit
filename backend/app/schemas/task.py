"""Task management schemas."""

from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
from app.models import TaskType, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    type: TaskType
    priority: str = "normal"
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    due_date: Optional[date] = None
    parent_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[str] = None
    category_id: Optional[int] = None
    project_id: Optional[int] = None
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    type: TaskType
    status: TaskStatus
    priority: str
    category_id: Optional[int]
    project_id: Optional[int]
    due_date: Optional[date]
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    children: list["TaskResponse"] = []

    @field_validator("children", mode="before")
    @classmethod
    def default_children(cls, v):
        return v if v is not None else []

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    total: int
    items: list[TaskResponse]
