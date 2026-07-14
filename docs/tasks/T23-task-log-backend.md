## 目标
实现任务日志（Task Log）功能，支持为每个任务添加学习笔记、问题记录、读后感等。

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建任务日志模型 (models/task_log.py)
```python
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class TaskLog(Base):
    __tablename__ = "task_logs"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    content = Column(Text, nullable=False)  # Markdown 内容
    log_type = Column(String(20), default="note")  # note/problem/knowledge/progress
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 2. 创建 Schema (schemas/task_log.py)
```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskLogCreate(BaseModel):
    task_id: int
    content: str
    log_type: str = "note"  # note/problem/knowledge/progress

class TaskLogUpdate(BaseModel):
    content: Optional[str] = None
    log_type: Optional[str] = None

class TaskLogResponse(BaseModel):
    id: int
    task_id: int
    content: str
    log_type: str
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True
```

### 3. 创建 API (api/task_logs.py)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.task_log import TaskLog
from app.schemas.task_log import TaskLogCreate, TaskLogUpdate, TaskLogResponse

router = APIRouter(prefix="/api/task-logs", tags=["任务日志"])

@router.get("/", response_model=List[TaskLogResponse])
def list_logs(
    task_id: Optional[int] = Query(None),
    log_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取日志列表，可按任务ID和类型筛选"""
    query = db.query(TaskLog)
    if task_id:
        query = query.filter(TaskLog.task_id == task_id)
    if log_type:
        query = query.filter(TaskLog.log_type == log_type)
    return query.order_by(TaskLog.created_at.desc()).limit(limit).all()

@router.get("/{log_id}", response_model=TaskLogResponse)
def get_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log

@router.post("/", response_model=TaskLogResponse)
def create_log(data: TaskLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = TaskLog(**data.dict())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.put("/{log_id}", response_model=TaskLogResponse)
def update_log(log_id: int, data: TaskLogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    for key, value in data.dict(exclude_unset=True).items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log

@router.delete("/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}

@router.get("/recent", response_model=List[TaskLogResponse])
def recent_logs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取最近的日志（用于仪表盘）"""
    return db.query(TaskLog).order_by(TaskLog.created_at.desc()).limit(limit).all()
```

### 4. 注册路由 (main.py)
```python
from app.api.task_logs import router as task_logs_router
app.include_router(task_logs_router)
```

### 5. 更新仪表盘 API (api/dashboard.py)
在 dashboard 返回值中添加：
```python
"recent_logs": db.query(TaskLog).order_by(TaskLog.created_at.desc()).limit(5).all()
```

### 6. 验收标准
- [ ] 数据库表创建成功
- [ ] 日志 CRUD API 正常
- [ ] 按任务ID筛选正常
- [ ] 按类型筛选正常
- [ ] 最近日志 API 正常
