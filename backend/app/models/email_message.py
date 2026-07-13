from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class EmailMessage(Base):
    """邮件消息模型"""
    __tablename__ = "email_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 关联邮箱账号
    account_id = Column(Integer, ForeignKey("email_accounts.id"), nullable=False, index=True)
    
    # 邮件标识
    message_id = Column(String(500), nullable=True, comment="邮件Message-ID")
    uid = Column(String(100), nullable=True, comment="IMAP UID")
    
    # 邮件内容
    subject = Column(String(500), nullable=True, comment="邮件主题")
    sender = Column(String(300), nullable=True, comment="发件人")
    recipients = Column(Text, nullable=True, comment="收件人列表(JSON)")
    cc = Column(Text, nullable=True, comment="抄送列表(JSON)")
    body_text = Column(Text, nullable=True, comment="纯文本正文")
    body_html = Column(Text, nullable=True, comment="HTML正文")
    
    # 状态
    is_read = Column(Boolean, default=False, comment="是否已读")
    is_starred = Column(Boolean, default=False, comment="是否星标")
    has_attachment = Column(Boolean, default=False, comment="是否有附件")
    
    # 文件夹
    folder = Column(String(100), nullable=True, comment="所在文件夹")
    
    # 时间
    received_at = Column(DateTime, nullable=True, comment="接收时间")
    created_at = Column(DateTime, server_default=func.now())
    
    # 关系
    account = relationship("EmailAccount", backref="messages")
