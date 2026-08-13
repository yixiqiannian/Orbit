from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class HotlistItemOut(BaseModel):
    id: int
    source: str
    rank: int
    title: str
    url: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars_today: Optional[int] = None
    stars_total: Optional[int] = None
    forks: Optional[int] = None
    hot_date: date
    created_at: datetime

    class Config:
        from_attributes = True


class HotlistResponse(BaseModel):
    date: date
    source: str
    items: list[HotlistItemOut]


class FetchResponse(BaseModel):
    message: str
    count: int
    date: date
