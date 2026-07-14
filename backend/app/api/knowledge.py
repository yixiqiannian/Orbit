"""Knowledge card API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import random

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.knowledge_category import KnowledgeCategory
from app.models.knowledge_card import KnowledgeCard
from app.schemas.knowledge import (
    CategoryCreate, CategoryResponse,
    CardCreate, CardUpdate, CardResponse,
    KnowledgeStatsResponse,
)

router = APIRouter(prefix="/api/knowledge", tags=["知识卡片"])


# ── 分类管理 ─────────────────────────────────────────


@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取分类列表（含卡片数量）."""
    categories = db.query(KnowledgeCategory).order_by(KnowledgeCategory.sort_order, KnowledgeCategory.id).all()
    result = []
    for cat in categories:
        card_count = db.query(KnowledgeCard).filter(KnowledgeCard.category_id == cat.id).count()
        result.append(CategoryResponse(
            id=cat.id, name=cat.name, icon=cat.icon, color=cat.color,
            sort_order=cat.sort_order, card_count=card_count,
        ))
    return result


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(request: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """创建分类."""
    category = KnowledgeCategory(**request.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryResponse(
        id=category.id, name=category.name, icon=category.icon, color=category.color,
        sort_order=category.sort_order, card_count=0,
    )


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除分类."""
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(category)
    db.commit()
    return {"message": "删除成功"}


# ── 卡片管理 ─────────────────────────────────────────


def _card_response(card: KnowledgeCard, db: Session) -> CardResponse:
    """Build a CardResponse with category_name populated."""
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == card.category_id).first()
    return CardResponse(
        id=card.id,
        category_id=card.category_id,
        category_name=category.name if category else "",
        title=card.title,
        content=card.content,
        tags=card.tags,
        created_at=card.created_at,
        updated_at=card.updated_at,
    )


@router.get("/cards", response_model=List[CardResponse])
def list_cards(
    category_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取卡片列表，支持按分类和关键词过滤."""
    query = db.query(KnowledgeCard)
    if category_id:
        query = query.filter(KnowledgeCard.category_id == category_id)
    if keyword:
        like_pattern = f"%{keyword}%"
        query = query.filter(
            (KnowledgeCard.title.like(like_pattern)) |
            (KnowledgeCard.content.like(like_pattern)) |
            (KnowledgeCard.tags.like(like_pattern))
        )
    cards = query.order_by(KnowledgeCard.updated_at.desc()).all()
    return [_card_response(card, db) for card in cards]


@router.get("/cards/{card_id}", response_model=CardResponse)
def get_card(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取单个卡片详情."""
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    return _card_response(card, db)


@router.post("/cards", response_model=CardResponse, status_code=201)
def create_card(request: CardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """创建卡片."""
    card = KnowledgeCard(**request.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return _card_response(card, db)


@router.put("/cards/{card_id}", response_model=CardResponse)
def update_card(card_id: int, request: CardUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """更新卡片."""
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(card, key, value)
    db.commit()
    db.refresh(card)
    return _card_response(card, db)


@router.delete("/cards/{card_id}")
def delete_card(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """删除卡片."""
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    db.delete(card)
    db.commit()
    return {"message": "删除成功"}


# ── 随机推送 ─────────────────────────────────────────


@router.get("/random", response_model=CardResponse)
def random_card(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """随机获取一张卡片."""
    cards = db.query(KnowledgeCard).all()
    if not cards:
        raise HTTPException(status_code=404, detail="暂无卡片")
    card = random.choice(cards)
    return _card_response(card, db)


# ── 统计 ─────────────────────────────────────────────


@router.get("/stats", response_model=KnowledgeStatsResponse)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取知识卡片统计数据."""
    total_cards = db.query(KnowledgeCard).count()
    total_categories = db.query(KnowledgeCategory).count()
    return KnowledgeStatsResponse(total_cards=total_cards, total_categories=total_categories)
