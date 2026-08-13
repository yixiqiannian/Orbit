from sqlalchemy import Column, Integer, String, Text, Date, DateTime, UniqueConstraint
from datetime import datetime
from app.core.database import Base


class HotlistItem(Base):
    __tablename__ = "hotlist_items"
    __table_args__ = (UniqueConstraint("source", "hot_date", "rank", name="uq_hotlist_source_date_rank"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(50), nullable=False, default="github")   # 数据源标识
    rank = Column(Integer, nullable=False)                           # 排名
    title = Column(String(300), nullable=False)                      # 仓库全名
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    stars_today = Column(Integer, nullable=True)                     # 今日新增 star
    stars_total = Column(Integer, nullable=True)
    forks = Column(Integer, nullable=True)
    hot_date = Column(Date, nullable=False)                          # 榜单日期
    created_at = Column(DateTime, default=datetime.utcnow)
