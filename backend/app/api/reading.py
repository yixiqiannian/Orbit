"""Reading (阅读规划) API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.book import Book, BookStatus
from app.schemas.reading import (
    BookCreate, BookUpdate, BookResponse, BookListResponse, ReadingStats
)

router = APIRouter(prefix="/api/reading", tags=["阅读规划"])


@router.get("/books", response_model=BookListResponse)
def list_books(
    status: Optional[BookStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取书籍列表."""
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
    """添加书籍."""
    book = Book(user_id=current_user.id, **request.dict())
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
    """获取书籍详情."""
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == current_user.id).first()
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
    """更新书籍."""
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == current_user.id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    for key, value in request.dict(exclude_unset=True).items():
        setattr(book, key, value)
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
    """删除书籍."""
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == current_user.id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    db.delete(book)
    db.commit()
    return {"message": "删除成功"}


@router.get("/stats", response_model=ReadingStats)
def get_reading_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取阅读统计."""
    total = db.query(Book).filter(Book.user_id == current_user.id).count()
    want = db.query(Book).filter(Book.user_id == current_user.id, Book.status == BookStatus.WANT_TO_READ).count()
    reading = db.query(Book).filter(Book.user_id == current_user.id, Book.status == BookStatus.READING).count()
    finished = db.query(Book).filter(Book.user_id == current_user.id, Book.status == BookStatus.FINISHED).count()
    avg_progress = db.query(func.avg(Book.progress)).filter(Book.user_id == current_user.id).scalar() or 0
    return ReadingStats(
        total_books=total,
        want_to_read=want,
        reading=reading,
        finished=finished,
        avg_progress=round(float(avg_progress), 1),
    )


@router.post("/sync")
async def sync_weread(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """同步微信读书书架."""
    from app.services.weread_client import get_weread_client

    client = get_weread_client()
    if not client:
        raise HTTPException(status_code=400, detail="微信读书 API 未配置，请在 .env 中设置 WEREAD_API_KEY")

    try:
        shelf_data = await client.get_shelf()
        books = shelf_data.get("books", [])
        synced = 0

        for item in books:
            weread_id = item.get("bookId")
            title = item.get("title", "")
            author = item.get("author", "")
            cover = item.get("cover", "")
            finish = item.get("finishReading", 0)

            # 获取阅读进度
            progress = 0
            last_read_at = None
            try:
                progress_data = await client.get_book_progress(weread_id)
                book_progress = progress_data.get("book", {})
                progress = book_progress.get("progress", 0)
                update_time = book_progress.get("updateTime")
                if update_time:
                    last_read_at = datetime.fromtimestamp(update_time)
            except Exception:
                pass

            # 检查是否已存在
            existing = db.query(Book).filter(
                Book.user_id == current_user.id,
                Book.weread_id == weread_id
            ).first()

            if existing:
                # 更新
                existing.title = title
                existing.author = author
                existing.cover_url = cover
                existing.progress = progress
                if last_read_at:
                    existing.last_read_at = last_read_at
                # 根据进度判断状态
                if progress >= 100:
                    existing.status = BookStatus.FINISHED
                elif progress > 0:
                    existing.status = BookStatus.READING
            else:
                # 新增
                if finish or progress >= 100:
                    status = BookStatus.FINISHED
                elif progress > 0:
                    status = BookStatus.READING
                else:
                    status = BookStatus.WANT_TO_READ

                book = Book(
                    user_id=current_user.id,
                    weread_id=weread_id,
                    title=title,
                    author=author,
                    cover_url=cover,
                    status=status,
                    progress=progress,
                    last_read_at=last_read_at,
                )
                db.add(book)
            synced += 1

        db.commit()
        return {"message": f"同步成功，共 {synced} 本书", "count": synced}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.get("/sync/{book_id}")
async def sync_book_progress(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """同步单本书的阅读进度."""
    from app.services.weread_client import get_weread_client

    client = get_weread_client()
    if not client:
        raise HTTPException(status_code=400, detail="微信读书 API 未配置")

    book = db.query(Book).filter(Book.id == book_id, Book.user_id == current_user.id).first()
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    if not book.weread_id:
        raise HTTPException(status_code=400, detail="非微信读书同步的书籍")

    try:
        progress_data = await client.get_book_progress(book.weread_id)
        book_progress = progress_data.get("book", {})
        progress = book_progress.get("progress", 0)
        update_time = book_progress.get("updateTime")

        book.progress = progress
        if update_time:
            book.last_read_at = datetime.fromtimestamp(update_time)
        if progress >= 100:
            book.status = BookStatus.FINISHED
        elif progress > 0:
            book.status = BookStatus.READING

        db.commit()
        db.refresh(book)
        return book
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")
