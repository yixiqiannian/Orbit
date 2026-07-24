from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User, Task, TaskType, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse

router = APIRouter(prefix="/api/tasks", tags=["任务管理"])


@router.get("", response_model=TaskListResponse)
def list_tasks(
    type: Optional[TaskType] = None,
    status: Optional[TaskStatus] = None,
    category_id: Optional[int] = None,
    project_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Task).filter(Task.user_id == current_user.id)
    if type:
        query = query.filter(Task.type == type)
    if status:
        query = query.filter(Task.status == status)
    if category_id is not None:
        query = query.filter(Task.category_id == category_id)
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)
    total = query.count()
    items = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return TaskListResponse(total=total, items=items)


@router.post("", response_model=TaskResponse)
def create_task(
    request: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = Task(user_id=current_user.id, **request.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/today", response_model=list[TaskResponse])
def get_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = (
        db.query(Task)
        .filter(
            Task.user_id == current_user.id,
            Task.type == TaskType.DAILY,
            Task.status != TaskStatus.COMPLETED,
        )
        .all()
    )
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    request: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    db.delete(task)
    db.commit()
    return {"message": "删除成功"}
