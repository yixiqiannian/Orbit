## 目标
实现邮箱管理的 API 接口，包括邮箱配置 CRUD、邮件列表、发送邮件等功能。

## 前置任务
依赖 T16 完成（需要数据库模型和 IMAP/SMTP 客户端）

## 工作目录
G:\Orbit\backend

## 任务要求

### 1. 创建邮箱 Schema (schemas/email.py)
```python
from pydantic import BaseModel
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
    password: str  # 授权码

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
    subject: str
    sender: str
    recipients: str
    body_text: Optional[str]
    is_read: bool
    is_starred: bool
    has_attachment: bool
    received_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SendEmailRequest(BaseModel):
    account_id: int
    to: List[str]
    subject: str
    body: str
    html: bool = False
    cc: Optional[List[str]] = None
```

### 2. 实现邮箱 API (api/email.py)
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/api/email", tags=["邮箱"])

@router.get("/accounts", response_model=List[EmailAccountResponse])
def list_accounts(db: Session, current_user = Depends(get_current_user)):
    """获取邮箱配置列表."""
    pass

@router.post("/accounts", response_model=EmailAccountResponse)
def create_account(request: EmailAccountCreate, db: Session, current_user = Depends(get_current_user)):
    """添加邮箱配置."""
    pass

@router.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session, current_user = Depends(get_current_user)):
    """删除邮箱配置."""
    pass

@router.get("/accounts/{account_id}/unread")
def get_unread_count(account_id: int, db: Session, current_user = Depends(get_current_user)):
    """获取未读邮件数量."""
    pass

@router.get("/accounts/{account_id}/messages")
def list_messages(account_id: int, folder: str = "INBOX", limit: int = 50, db: Session, current_user = Depends(get_current_user)):
    """获取邮件列表."""
    pass

@router.post("/accounts/{account_id}/send")
def send_email(account_id: int, request: SendEmailRequest, db: Session, current_user = Depends(get_current_user)):
    """发送邮件."""
    pass

@router.put("/messages/{message_id}/read")
def mark_as_read(message_id: int, db: Session, current_user = Depends(get_current_user)):
    """标记邮件为已读."""
    pass

@router.post("/accounts/{account_id}/sync")
def sync_emails(account_id: int, db: Session, current_user = Depends(get_current_user)):
    """同步邮件."""
    pass
```

### 3. 注册路由到 main.py

## 验收标准
- [ ] 邮箱配置 CRUD 接口正常
- [ ] 获取未读数量接口正常
- [ ] 邮件列表接口正常
- [ ] 发送邮件接口正常
- [ ] 同步邮件接口正常
