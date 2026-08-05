from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)  # 日期
    title = Column(String(200), default="")  # 标题
    content = Column(Text, nullable=False)  # Markdown 内容
    mood = Column(String(20), default="normal")  # 心情：good/normal/bad
    tags = Column(String(500), default="")  # 标签，逗号分隔
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
