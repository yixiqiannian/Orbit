from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class TaskCategory(Base):
    __tablename__ = "task_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)  # 分类名称
    icon = Column(String(50), default="📋")  # 图标
    color = Column(String(20), default="#409EFF")  # 颜色
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
