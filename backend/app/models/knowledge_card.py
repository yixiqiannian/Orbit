"""Knowledge card model."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class KnowledgeCard(Base):
    __tablename__ = "knowledge_cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("knowledge_categories.id"), nullable=False)
    title = Column(String(200), nullable=False, comment="卡片标题")
    content = Column(Text, nullable=False, comment="Markdown 内容")
    tags = Column(String(500), default="", comment="标签，逗号分隔")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("KnowledgeCategory", backref="cards")
