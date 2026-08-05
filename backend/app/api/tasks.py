from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta

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
    archived: Optional[bool] = None,
    archived_month: Optional[str] = None,
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
    if archived is not None:
        query = query.filter(Task.archived == archived)
    if archived_month:
        query = query.filter(Task.archived_month == archived_month)
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


@router.post("/archive")
def archive_tasks(
    month: str = Query(None, description="归档月份，如 2026-07，不传则归档上月"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """归档已完成的任务"""
    if not month:
        # 默认归档上月
        today = datetime.now()
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        month = last_day_last_month.strftime("%Y-%m")

    # 查找需要归档的任务
    # 条件：status=completed, created_at 在指定月份, 未归档
    year, month_num = map(int, month.split('-'))
    start_date = datetime(year, month_num, 1)
    if month_num == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month_num + 1, 1)

    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.COMPLETED,
        Task.created_at >= start_date,
        Task.created_at < end_date,
        Task.archived == False
    ).all()

    for task in tasks:
        task.archived = True
        task.archived_month = month

    db.commit()

    return {
        "message": f"已归档 {len(tasks)} 个任务到 {month}",
        "count": len(tasks),
        "month": month
    }


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
