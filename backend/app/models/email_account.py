from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class EmailAccount(Base):
    """邮箱账号配置模型"""
    __tablename__ = "email_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 基本信息
    name = Column(String(100), nullable=False, comment="邮箱名称")
    email = Column(String(200), unique=True, nullable=False, index=True, comment="邮箱地址")
    
    # IMAP 配置
    imap_server = Column(String(200), nullable=False, comment="IMAP服务器地址")
    imap_port = Column(Integer, default=993, comment="IMAP端口")
    imap_ssl = Column(Boolean, default=True, comment="IMAP是否使用SSL")
    
    # SMTP 配置
    smtp_server = Column(String(200), nullable=False, comment="SMTP服务器地址")
    smtp_port = Column(Integer, default=465, comment="SMTP端口")
    smtp_ssl = Column(Boolean, default=True, comment="SMTP是否使用SSL")
    
    # 认证信息
    username = Column(String(200), nullable=False, comment="登录用户名")
    password_encrypted = Column(String(500), nullable=False, comment="加密后的密码/授权码")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
