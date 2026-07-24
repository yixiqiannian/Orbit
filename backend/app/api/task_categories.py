"""Task Categories API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.task_category import TaskCategory
from app.models.task import Task
from app.schemas.task_category import TaskCategoryCreate, TaskCategoryResponse

router = APIRouter(prefix="/api/task-categories", tags=["任务分类"])


@router.get("/", response_model=List[TaskCategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务分类列表"""
    categories = (
        db.query(TaskCategory).order_by(TaskCategory.sort_order).all()
    )
    return categories


@router.post("/", response_model=TaskCategoryResponse)
def create_category(
    request: TaskCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建任务分类"""
    # 检查名称是否重复
    existing = (
        db.query(TaskCategory).filter(TaskCategory.name == request.name).first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="分类名称已存在")

    # 获取最大排序号
    max_order = db.query(TaskCategory).count()

    category = TaskCategory(
        **request.model_dump(),
        sort_order=max_order,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除任务分类"""
    category = db.query(TaskCategory).filter(TaskCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")

    # 将该分类下的任务的 category_id 置空
    db.query(Task).filter(Task.category_id == category_id).update(
        {"category_id": None}
    )

    db.delete(category)
    db.commit()
    return {"message": "删除成功"}
