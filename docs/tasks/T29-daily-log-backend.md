## 目标
实现每日日志功能，用于记录工作总结、学习笔记等。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建日志模型 (models/daily_log.py)
```python
from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class DailyLog(Base):
    __tablename__ = "daily_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)  # 日期
    title = Column(String(200), default="")  # 标题
    content = Column(Text, nullable=False)  # Markdown 内容
    mood = Column(String(20), default="normal")  # 心情：good/normal/bad
    tags = Column(String(500), default="")  # 标签，逗号分隔
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 2. 创建 Schema (schemas/daily_log.py)
```python
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class DailyLogCreate(BaseModel):
    date: date
    title: str = ""
    content: str
    mood: str = "normal"
    tags: str = ""

class DailyLogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    tags: Optional[str] = None

class DailyLogResponse(BaseModel):
    id: int
    date: date
    title: str
    content: str
    mood: str
    tags: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
```

### 3. 创建 API (api/daily_logs.py)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.daily_log import DailyLog
from app.schemas.daily_log import DailyLogCreate, DailyLogUpdate, DailyLogResponse

router = APIRouter(prefix="/api/daily-logs", tags=["每日日志"])

@router.get("/", response_model=List[DailyLogResponse])
def list_logs(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(DailyLog)
    if start_date:
        query = query.filter(DailyLog.date >= start_date)
    if end_date:
        query = query.filter(DailyLog.date <= end_date)
    return query.order_by(DailyLog.date.desc()).limit(limit).all()

@router.get("/recent", response_model=List[DailyLogResponse])
def recent_logs(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(DailyLog).order_by(DailyLog.date.desc()).limit(limit).all()

@router.get("/{log_id}", response_model=DailyLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(DailyLog).filter(DailyLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log

@router.post("/", response_model=DailyLogResponse)
def create_log(data: DailyLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = DailyLog(**data.dict())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.put("/{log_id}", response_model=DailyLogResponse)
def update_log(log_id: int, data: DailyLogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(DailyLog).filter(DailyLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log

@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(DailyLog).filter(DailyLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}
```

### 4. 注册路由 (main.py)
```python
from app.api.daily_logs import router as daily_logs_router
app.include_router(daily_logs_router)
```

### 5. 更新仪表盘 API (api/dashboard.py)
添加最近日志：
```python
from app.models.daily_log import DailyLog

# 在 get_stats 函数中
recent_logs = db.query(DailyLog).order_by(DailyLog.date.desc()).limit(5).all()
```

### 6. 验收标准
- [ ] 数据库表创建成功
- [ ] 日志 CRUD API 正常
- [ ] 按日期筛选正常
- [ ] 最近日志 API 正常
