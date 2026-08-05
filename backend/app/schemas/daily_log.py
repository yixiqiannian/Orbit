from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class DailyLogCreate(BaseModel):
    date: date
    title: str = ""
    content: str
    mood: str = "normal"
    tags: str = ""


class DailyLogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[str] = None


class DailyLogResponse(BaseModel):
    id: int
    date: date
    title: str
    content: str
    mood: str
    tags: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
