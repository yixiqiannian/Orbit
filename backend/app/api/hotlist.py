"""热榜 API."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.hotlist_item import HotlistItem
from app.schemas.hotlist import HotlistResponse, FetchResponse

router = APIRouter(prefix="/api/hotlist", tags=["热榜"])

# 数据源注册表（扩展新源时在这里加）
SOURCES = [
    {"key": "github", "name": "GitHub Trending", "url": "https://github.com/trending"},
]


@router.get("/sources/")
def list_sources(current_user: User = Depends(get_current_user)):
    """列出可用数据源。"""
    return {"sources": SOURCES}


@router.get("/", response_model=HotlistResponse)
def get_hotlist(
    source: str = Query("github"),
    hot_date: Optional[date] = Query(None, description="榜单日期，默认今天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """查询某日热榜。"""
    d = hot_date or date.today()
    items = (
        db.query(HotlistItem)
        .filter(HotlistItem.source == source, HotlistItem.hot_date == d)
        .order_by(HotlistItem.rank.asc())
        .all()
    )
    return HotlistResponse(date=d, source=source, items=items)


@router.post("/fetch/", response_model=FetchResponse)
def fetch_hotlist(
    source: str = Query("github"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """抓取指定源最新热榜并入库（按 source+date+rank 去重，已有数据跳过）。"""
    if source != "github":
        raise HTTPException(status_code=400, detail=f"暂不支持数据源: {source}")
    from app.services.github_trending import fetch_trending
    import asyncio

    try:
        items = asyncio.run(fetch_trending())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"抓取失败: {e}")
    today = date.today()
    added = 0
    for it in items:
        exists = (
            db.query(HotlistItem)
            .filter(
                HotlistItem.source == source,
                HotlistItem.hot_date == today,
                HotlistItem.rank == it["rank"],
            )
            .first()
        )
        if exists:
            continue
        db.add(HotlistItem(source=source, hot_date=today, **it))
        added += 1
    db.commit()
    return FetchResponse(message=f"抓取完成，新增 {added} 条", count=added, date=today)
