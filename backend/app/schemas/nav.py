"""Navigation module schemas."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


# ── Category schemas ──────────────────────────────────────────


class NavCategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None
    sort_order: int = 0


class NavCategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class NavCategoryResponse(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── Site schemas ──────────────────────────────────────────────


class NavSiteCreate(BaseModel):
    category_id: int
    name: str
    url: str
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class NavSiteUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None


class NavSiteResponse(BaseModel):
    id: int
    category_id: int
    name: str
    url: str
    icon: Optional[str]
    description: Optional[str]
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── List / stats schemas ─────────────────────────────────────


class NavSiteListResponse(BaseModel):
    total: int
    items: List[NavSiteResponse]


class NavStatsResponse(BaseModel):
    total_categories: int
    total_sites: int
