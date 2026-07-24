"""Projects API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task, TaskStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/api/projects", tags=["项目"])


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取项目列表，包含任务统计"""
    query = db.query(Project)

    if status:
        query = query.filter(Project.status == status)

    projects = query.order_by(Project.created_at.desc()).all()

    # 计算每个项目的任务统计
    result = []
    for project in projects:
        task_count = db.query(Task).filter(Task.project_id == project.id).count()
        completed_count = (
            db.query(Task)
            .filter(Task.project_id == project.id, Task.status == TaskStatus.COMPLETED)
            .count()
        )
        project_data = ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            start_date=project.start_date,
            end_date=project.end_date,
            task_count=task_count,
            completed_count=completed_count,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
        result.append(project_data)

    return result


@router.post("", response_model=ProjectResponse)
def create_project(
    request: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建项目"""
    project = Project(**request.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        task_count=0,
        completed_count=0,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取单个项目详情"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    completed_count = (
        db.query(Task)
        .filter(Task.project_id == project.id, Task.status == TaskStatus.COMPLETED)
        .count()
    )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        task_count=task_count,
        completed_count=completed_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    request: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)

    task_count = db.query(Task).filter(Task.project_id == project.id).count()
    completed_count = (
        db.query(Task)
        .filter(Task.project_id == project.id, Task.status == TaskStatus.COMPLETED)
        .count()
    )

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        task_count=task_count,
        completed_count=completed_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除项目"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 将项目下的任务的 project_id 置空
    db.query(Task).filter(Task.project_id == project_id).update({"project_id": None})

    db.delete(project)
    db.commit()
    return {"message": "删除成功"}
