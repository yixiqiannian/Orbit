import enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class BookStatus(str, enum.Enum):
    WANT_TO_READ = "want_to_read"
    READING = "reading"
    FINISHED = "finished"


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weread_id = Column(String(100))
    title = Column(String(200), nullable=False)
    author = Column(String(100))
    cover_url = Column(String(500))
    status = Column(Enum(BookStatus), default=BookStatus.WANT_TO_READ)
    progress = Column(Integer, default=0)
    total_chapters = Column(Integer)
    current_chapter = Column(Integer)
    notes = Column(Text)
    last_read_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="books")
