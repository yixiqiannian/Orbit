"""Navigation site model."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class NavSite(Base):
    __tablename__ = "nav_sites"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("nav_categories.id"), nullable=False)
    name = Column(String(200), nullable=False, comment="网站名称")
    url = Column(String(500), nullable=False, comment="网站地址")
    icon = Column(String(500), nullable=True, comment="图标URL")
    description = Column(String(500), nullable=True, comment="描述")
    sort_order = Column(Integer, default=0, comment="排序")
    created_at = Column(DateTime, server_default=func.now())

    category = relationship("NavCategory", backref="sites")
