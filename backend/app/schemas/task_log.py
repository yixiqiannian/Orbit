from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskLogCreate(BaseModel):
    task_id: int
    content: str
    log_type: str = "note"  # note/problem/knowledge/progress


class TaskLogUpdate(BaseModel):
    content: Optional[str] = None
    log_type: Optional[str] = None


class TaskLogResponse(BaseModel):
    id: int
    task_id: int
    content: str
    log_type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
