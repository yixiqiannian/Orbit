import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base


class ExecutionStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"


class CronExecution(Base):
    __tablename__ = "cron_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cron_job_id = Column(String(100), nullable=False, index=True)
    cron_job_name = Column(String(200))
    status = Column(Enum(ExecutionStatus), nullable=False)
    result = Column(Text)
    error_message = Column(Text)
    executed_at = Column(DateTime, server_default=func.now())
