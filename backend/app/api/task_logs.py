from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.task_log import TaskLog
from app.schemas.task_log import TaskLogCreate, TaskLogUpdate, TaskLogResponse

router = APIRouter(prefix="/api/task-logs", tags=["任务日志"])


@router.get("/recent", response_model=List[TaskLogResponse])
def recent_logs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取最近的日志（用于仪表盘）"""
    return db.query(TaskLog).order_by(TaskLog.created_at.desc()).limit(limit).all()


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
def get_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    return log


@router.post("/", response_model=TaskLogResponse)
def create_log(
    data: TaskLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = TaskLog(**data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.put("/{log_id}", response_model=TaskLogResponse)
def update_log(
    log_id: int,
    data: TaskLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}")
def delete_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = db.query(TaskLog).filter(TaskLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="日志不存在")
    db.delete(log)
    db.commit()
    return {"message": "删除成功"}
