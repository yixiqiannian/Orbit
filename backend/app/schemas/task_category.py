"""TaskCategory schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskCategoryCreate(BaseModel):
    name: str
    icon: str = "📋"
    color: str = "#409EFF"


class TaskCategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True
