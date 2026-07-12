from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.book import Book, BookStatus
from app.schemas.reading import (
    BookCreate, BookUpdate, BookResponse, BookListResponse, ReadingStats,
)

router = APIRouter(prefix="/api/reading", tags=["阅读规划"])


# ── 书籍 CRUD ────────────────────────────────────────────────────────────

@router.get("/books", response_model=BookListResponse)
def list_books(
    status: Optional[BookStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """按状态筛选书籍列表，支持分页。"""
    query = db.query(Book).filter(Book.user_id == current_user.id)
    if status:
        query = query.filter(Book.status == status)
    total = query.count()
    items = query.order_by(Book.updated_at.desc()).offset((page - 1) * size).limit(size).all()
    return BookListResponse(total=total, items=items)


@router.post("/books", response_model=BookResponse)
def create_book(
    request: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加新书籍到书架。"""
    book = Book(user_id=current_user.id, **request.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单本书籍详情。"""
    book = db.query(Book).filter(
        Book.id == book_id, Book.user_id == current_user.id
    ).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return book


@router.put("/books/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    request: BookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新书籍信息（标题、状态、进度等）。"""
    book = db.query(Book).filter(
        Book.id == book_id, Book.user_id == current_user.id
    ).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(book, key, value)

    # 首次标记为"在读"时，自动记录 last_read_at
    if request.status == BookStatus.READING and not book.last_read_at:
        book.last_read_at = datetime.utcnow()

    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}")
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除书籍。"""
    book = db.query(Book).filter(
        Book.id == book_id, Book.user_id == current_user.id
    ).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    db.delete(book)
    db.commit()
    return {"message": "删除成功"}


# ── 阅读统计 ─────────────────────────────────────────────────────────────

@router.get("/stats", response_model=ReadingStats)
def get_reading_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """返回当前用户的阅读统计数据。"""
    uid = current_user.id
    total = db.query(Book).filter(Book.user_id == uid).count()
    want = db.query(Book).filter(Book.user_id == uid, Book.status == BookStatus.WANT_TO_READ).count()
    reading = db.query(Book).filter(Book.user_id == uid, Book.status == BookStatus.READING).count()
    finished = db.query(Book).filter(Book.user_id == uid, Book.status == BookStatus.FINISHED).count()
    avg_progress = db.query(func.avg(Book.progress)).filter(Book.user_id == uid).scalar() or 0
    return ReadingStats(
        total_books=total,
        want_to_read=want,
        reading=reading,
        finished=finished,
        avg_progress=round(float(avg_progress), 1),
    )


# ── 微信读书同步（预留） ────────────────────────────────────────────────

@router.post("/sync")
async def sync_weread(current_user: User = Depends(get_current_user)):
    """同步微信读书书架（预留接口）"""
    # TODO: 实现微信读书同步逻辑
    return {"message": "同步功能开发中"}
