from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.book import BookStatus


class BookCreate(BaseModel):
    title: str
    author: Optional[str] = None
    cover_url: Optional[str] = None
    status: BookStatus = BookStatus.WANT_TO_READ
    total_chapters: Optional[int] = None
    notes: Optional[str] = None


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    cover_url: Optional[str] = None
    status: Optional[BookStatus] = None
    progress: Optional[int] = None
    current_chapter: Optional[int] = None
    notes: Optional[str] = None


class BookResponse(BaseModel):
    id: int
    weread_id: Optional[str]
    title: str
    author: Optional[str]
    cover_url: Optional[str]
    status: BookStatus
    progress: int
    total_chapters: Optional[int]
    current_chapter: Optional[int]
    notes: Optional[str]
    last_read_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    total: int
    items: list[BookResponse]


class ReadingStats(BaseModel):
    total_books: int
    want_to_read: int
    reading: int
    finished: int
    avg_progress: float
