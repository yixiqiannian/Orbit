import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TaskType(str, enum.Enum):
    DAILY = "daily"
    PLAN = "plan"
    GOAL = "goal"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(String(20), default="normal")  # low/normal/high/urgent
    category_id = Column(Integer, ForeignKey("task_categories.id"), nullable=True)  # 分类
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # 项目
    due_date = Column(Date)
    parent_id = Column(Integer, ForeignKey("tasks.id"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="tasks")
    children = relationship("Task", backref="parent", remote_side=[id])
    category = relationship("TaskCategory", backref="tasks")
    project = relationship("Project", backref="tasks")
