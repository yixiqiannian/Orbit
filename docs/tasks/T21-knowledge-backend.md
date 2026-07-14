## 目标
实现知识卡片（记忆卡片）模块的数据库模型和 API。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建分类模型 (models/knowledge_category.py)
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class KnowledgeCategory(Base):
    __tablename__ = "knowledge_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # 分类名称
    icon = Column(String(50), default="📚")  # 图标
    color = Column(String(20), default="#409EFF")  # 颜色
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
```

### 2. 创建卡片模型 (models/knowledge_card.py)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class KnowledgeCard(Base):
    __tablename__ = "knowledge_cards"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=False)
    title = Column(String(200), nullable=False)  # 卡片标题
    content = Column(Text, nullable=False)  # Markdown 内容
    tags = Column(String(500), default="")  # 标签，逗号分隔
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 3. 创建 Schema (schemas/knowledge.py)
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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
    card_count: int = 0  # 该分类下的卡片数量
    class Config:
        from_attributes = True

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
    category_name: str = ""  # 分类名称
    title: str
    content: str
    tags: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
```

### 4. 创建 API (api/knowledge.py)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import random

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.knowledge_category import KnowledgeCategory
from app.models.knowledge_card import KnowledgeCard
from app.schemas.knowledge import (
    CategoryCreate, CategoryResponse,
    CardCreate, CardUpdate, CardResponse
)

router = APIRouter(prefix="/api/knowledge", tags=["知识卡片"])

# 分类 CRUD
@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    categories = db.query(KnowledgeCategory).order_by(KnowledgeCategory.sort_order).all()
    result = []
    for cat in categories:
        card_count = db.query(KnowledgeCard).filter(KnowledgeCard.category_id == cat.id).count()
        result.append(CategoryResponse(**cat.__dict__, card_count=card_count))
    return result

@router.post("/categories", response_model=CategoryResponse)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = KnowledgeCategory(**data.dict())
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryResponse(**category.__dict__, card_count=0)

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    db.delete(category)
    db.commit()
    return {"message": "删除成功"}

# 卡片 CRUD
@router.get("/cards", response_model=list[CardResponse])
def list_cards(
    category_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(KnowledgeCard)
    if category_id:
        query = query.filter(KnowledgeCard.category_id == category_id)
    if keyword:
        query = query.filter(
            (KnowledgeCard.title.contains(keyword)) |
            (KnowledgeCard.content.contains(keyword)) |
            (KnowledgeCard.tags.contains(keyword))
        )
    cards = query.order_by(KnowledgeCard.updated_at.desc()).all()
    result = []
    for card in cards:
        category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == card.category_id).first()
        result.append(CardResponse(**card.__dict__, category_name=category.name if category else ""))
    return result

@router.get("/cards/{card_id}", response_model=CardResponse)
def get_card(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == card.category_id).first()
    return CardResponse(**card.__dict__, category_name=category.name if category else "")

@router.post("/cards", response_model=CardResponse)
def create_card(data: CardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    card = KnowledgeCard(**data.dict())
    db.add(card)
    db.commit()
    db.refresh(card)
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == card.category_id).first()
    return CardResponse(**card.__dict__, category_name=category.name if category else "")

@router.put("/cards/{card_id}", response_model=CardResponse)
def update_card(card_id: int, data: CardUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(card, key, value)
    db.commit()
    db.refresh(card)
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == card.category_id).first()
    return CardResponse(**card.__dict__, category_name=category.name if category else "")

@router.delete("/cards/{card_id}")
def delete_card(card_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    card = db.query(KnowledgeCard).filter(KnowledgeCard.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="卡片不存在")
    db.delete(card)
    db.commit()
    return {"message": "删除成功"}

# 随机推送
@router.get("/random", response_model=CardResponse)
def random_card(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cards = db.query(KnowledgeCard).all()
    if not cards:
        raise HTTPException(status_code=404, detail="暂无卡片")
    card = random.choice(cards)
    category = db.query(KnowledgeCategory).filter(KnowledgeCategory.id == card.category_id).first()
    return CardResponse(**card.__dict__, category_name=category.name if category else "")

# 统计
@router.get("/stats")
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_cards = db.query(KnowledgeCard).count()
    total_categories = db.query(KnowledgeCategory).count()
    return {"total_cards": total_cards, "total_categories": total_categories}
```

### 5. 注册路由 (main.py)
在 main.py 中添加:
```python
from app.api.knowledge import router as knowledge_router
app.include_router(knowledge_router)
```

### 6. 验收标准
- [ ] 数据库表创建成功
- [ ] 分类 CRUD API 正常
- [ ] 卡片 CRUD API 正常
- [ ] 随机推送 API 正常
- [ ] 统计 API 正常
