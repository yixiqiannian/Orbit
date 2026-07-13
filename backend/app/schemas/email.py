"""Email module schemas."""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class EmailAccountCreate(BaseModel):
    name: str
    email: str
    imap_server: str
    imap_port: int = 993
    imap_ssl: bool = True
    smtp_server: str
    smtp_port: int = 465
    smtp_ssl: bool = True
    username: str
    password: str  # 授权码/密码，存储时加密


class EmailAccountUpdate(BaseModel):
    name: Optional[str] = None
    imap_server: Optional[str] = None
    imap_port: Optional[int] = None
    imap_ssl: Optional[bool] = None
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_ssl: Optional[bool] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class EmailAccountResponse(BaseModel):
    id: int
    name: str
    email: str
    imap_server: str
    smtp_server: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EmailMessageResponse(BaseModel):
    id: int
    account_id: int
    subject: Optional[str]
    sender: Optional[str]
    recipients: Optional[str]
    body_text: Optional[str]
    is_read: bool
    is_starred: bool
    has_attachment: bool
    folder: Optional[str]
    received_at: Optional[datetime]

    class Config:
        from_attributes = True


class EmailMessageListResponse(BaseModel):
    total: int
    items: List[EmailMessageResponse]


class SendEmailRequest(BaseModel):
    to: List[str]
    subject: str
    body: str
    html: bool = False
    cc: Optional[List[str]] = None
