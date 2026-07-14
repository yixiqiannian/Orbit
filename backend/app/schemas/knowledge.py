"""Knowledge module schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ── Category schemas ──────────────────────────────────────────


class CategoryCreate(BaseModel):
    name: str
    icon: str = "📚"
    color: str = "#409EFF"
    sort_order: int = 0


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    sort_order: int
    card_count: int = 0

    class Config:
        from_attributes = True


# ── Card schemas ──────────────────────────────────────────────


class CardCreate(BaseModel):
    category_id: int
    title: str
    content: str
    tags: str = ""


class CardUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None


class CardResponse(BaseModel):
    id: int
    category_id: int
    category_name: str = ""
    title: str
    content: str
    tags: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ── Stats schema ──────────────────────────────────────────────


class KnowledgeStatsResponse(BaseModel):
    total_cards: int
    total_categories: int
