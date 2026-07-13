"""Navigation API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.models.nav_category import NavCategory
from app.models.nav_site import NavSite
from app.schemas.nav import (
    NavCategoryCreate,
    NavCategoryUpdate,
    NavCategoryResponse,
    NavSiteCreate,
    NavSiteUpdate,
    NavSiteResponse,
    NavSiteListResponse,
    NavStatsResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nav", tags=["导航"])


# ── Category CRUD ─────────────────────────────────────────────


@router.get("/categories", response_model=List[NavCategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取分类列表."""
    categories = db.query(NavCategory).order_by(NavCategory.sort_order, NavCategory.id).all()
    return categories


@router.post("/categories", response_model=NavCategoryResponse, status_code=201)
def create_category(
    request: NavCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建分类."""
    category = NavCategory(
        name=request.name,
        icon=request.icon,
        sort_order=request.sort_order,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=NavCategoryResponse)
def update_category(
    category_id: int,
    request: NavCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新分类."""
    category = db.query(NavCategory).filter(NavCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除分类."""
    category = db.query(NavCategory).filter(NavCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    # 检查分类下是否有导航站点
    site_count = db.query(NavSite).filter(NavSite.category_id == category_id).count()
    if site_count > 0:
        raise HTTPException(status_code=409, detail=f"该分类下有 {site_count} 个站点，请先删除站点")
    db.delete(category)
    db.commit()
    return {"message": "删除成功"}


# ── Site CRUD ─────────────────────────────────────────────────


@router.get("/sites", response_model=NavSiteListResponse)
def list_sites(
    category_id: Optional[int] = Query(None, description="按分类筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取导航列表（可按分类筛选）."""
    query = db.query(NavSite)
    if category_id is not None:
        query = query.filter(NavSite.category_id == category_id)
    total = query.count()
    items = query.order_by(NavSite.sort_order, NavSite.id).all()
    return NavSiteListResponse(total=total, items=items)


@router.post("/sites", response_model=NavSiteResponse, status_code=201)
def create_site(
    request: NavSiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建导航."""
    # 验证分类存在
    category = db.query(NavCategory).filter(NavCategory.id == request.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    site = NavSite(
        category_id=request.category_id,
        name=request.name,
        url=request.url,
        icon=request.icon,
        description=request.description,
        sort_order=request.sort_order,
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.put("/sites/{site_id}", response_model=NavSiteResponse)
def update_site(
    site_id: int,
    request: NavSiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新导航."""
    site = db.query(NavSite).filter(NavSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="导航站点不存在")
    update_data = request.model_dump(exclude_unset=True)
    # 如果更新了分类，验证分类存在
    if "category_id" in update_data:
        category = db.query(NavCategory).filter(NavCategory.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
    for key, value in update_data.items():
        setattr(site, key, value)
    db.commit()
    db.refresh(site)
    return site


@router.delete("/sites/{site_id}")
def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除导航."""
    site = db.query(NavSite).filter(NavSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="导航站点不存在")
    db.delete(site)
    db.commit()
    return {"message": "删除成功"}


# ── Stats ─────────────────────────────────────────────────────


@router.get("/stats", response_model=NavStatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取统计数据."""
    total_categories = db.query(NavCategory).count()
    total_sites = db.query(NavSite).count()
    return NavStatsResponse(total_categories=total_categories, total_sites=total_sites)
