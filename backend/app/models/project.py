from sqlalchemy import Column, Integer, String, Text, DateTime, Date
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # 项目名称
    description = Column(Text, default="")  # 项目描述
    status = Column(String(20), default="active")  # active/completed/archived
    start_date = Column(Date, nullable=True)  # 开始日期
    end_date = Column(Date, nullable=True)  # 结束日期
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
