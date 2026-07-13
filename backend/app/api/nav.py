"""Navigation API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, NavCategory, NavSite
from app.schemas.nav import (
    NavCategoryCreate, NavCategoryUpdate, NavCategoryResponse,
    NavSiteCreate, NavSiteUpdate, NavSiteResponse, NavStats
)

router = APIRouter(prefix="/api/nav", tags=["导航"])


def get_favicon_url(url: str) -> str:
    """获取网站 favicon."""
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        return f"{base_url}/favicon.ico"
    except:
        return ""


async def fetch_site_info(url: str) -> dict:
    """获取网站标题和图标."""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 获取标题
            title = ""
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # 获取图标
            icon = ""
            # 尝试从 link 标签获取
            icon_tag = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
            if icon_tag and icon_tag.get('href'):
                icon = urljoin(url, icon_tag['href'])
            else:
                # 使用默认 favicon
                icon = get_favicon_url(url)
            
            return {"title": title, "icon": icon}
    except Exception as e:
        return {"title": "", "icon": get_favicon_url(url)}


# ── 分类管理 ─────────────────────────────────────────


@router.get("/categories", response_model=List[NavCategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取分类列表."""
    return db.query(NavCategory).order_by(NavCategory.sort_order, NavCategory.id).all()


@router.post("/categories", response_model=NavCategoryResponse, status_code=201)
def create_category(request: NavCategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """创建分类."""
    category = NavCategory(**request.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=NavCategoryResponse)
def update_category(category_id: int, request: NavCategoryUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新分类."""
    category = db.query(NavCategory).filter(NavCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除分类."""
    category = db.query(NavCategory).filter(NavCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(category)
    db.commit()
    return {"message": "删除成功"}


# ── 导航管理 ─────────────────────────────────────────


@router.get("/sites", response_model=List[NavSiteResponse])
def list_sites(category_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取导航列表."""
    query = db.query(NavSite)
    if category_id:
        query = query.filter(NavSite.category_id == category_id)
    return query.order_by(NavSite.sort_order, NavSite.id).all()


@router.post("/sites", response_model=NavSiteResponse, status_code=201)
async def create_site(request: NavSiteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """创建导航."""
    # 如果没有提供标题和图标，自动获取
    title = request.name
    icon = request.icon
    
    if not title or not icon:
        info = await fetch_site_info(str(request.url))
        if not title:
            title = info.get("title", "") or urlparse(str(request.url)).netloc
        if not icon:
            icon = info.get("icon", "")
    
    site = NavSite(
        category_id=request.category_id,
        name=title,
        url=str(request.url),
        icon=icon,
        description=request.description,
        sort_order=request.sort_order
    )
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.put("/sites/{site_id}", response_model=NavSiteResponse)
def update_site(site_id: int, request: NavSiteUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新导航."""
    site = db.query(NavSite).filter(NavSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="导航不存在")
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(site, key, value)
    db.commit()
    db.refresh(site)
    return site


@router.delete("/sites/{site_id}")
def delete_site(site_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除导航."""
    site = db.query(NavSite).filter(NavSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="导航不存在")
    db.delete(site)
    db.commit()
    return {"message": "删除成功"}


@router.post("/fetch-info")
async def fetch_info(url: str):
    """获取网站信息（标题和图标）."""
    info = await fetch_site_info(url)
    return info


@router.get("/stats", response_model=NavStats)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取统计数据."""
    categories = db.query(NavCategory).count()
    sites = db.query(NavSite).count()
    return NavStats(categories=categories, sites=sites)
