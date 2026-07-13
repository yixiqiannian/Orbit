"""Email API endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.encryption import encrypt, decrypt
from app.models import User, EmailAccount, EmailMessage
from app.schemas.email import (
    EmailAccountCreate,
    EmailAccountUpdate,
    EmailAccountResponse,
    EmailMessageResponse,
    EmailMessageListResponse,
    SendEmailRequest,
)
from app.services.imap_client import ImapClient
from app.services.smtp_client import SmtpClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/email", tags=["邮箱"])


def _get_account_or_404(account_id: int, db: Session, user: User) -> EmailAccount:
    """Fetch an email account owned by the user or raise 404."""
    account = (
        db.query(EmailAccount)
        .filter(EmailAccount.id == account_id)
        .first()
    )
    if not account:
        raise HTTPException(status_code=404, detail="邮箱配置不存在")
    return account


# ── 邮箱配置 CRUD ────────────────────────────────────────────


@router.get("/accounts", response_model=List[EmailAccountResponse])
def list_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮箱配置列表."""
    accounts = db.query(EmailAccount).filter(EmailAccount.is_active == True).all()
    return accounts


@router.post("/accounts", response_model=EmailAccountResponse, status_code=201)
def create_account(
    request: EmailAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加邮箱配置."""
    # 检查邮箱地址是否已存在
    existing = db.query(EmailAccount).filter(EmailAccount.email == request.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="该邮箱地址已存在")

    account = EmailAccount(
        name=request.name,
        email=request.email,
        imap_server=request.imap_server,
        imap_port=request.imap_port,
        imap_ssl=request.imap_ssl,
        smtp_server=request.smtp_server,
        smtp_port=request.smtp_port,
        smtp_ssl=request.smtp_ssl,
        username=request.username,
        password_encrypted=encrypt(request.password),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/accounts/{account_id}", response_model=EmailAccountResponse)
def update_account(
    account_id: int,
    request: EmailAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新邮箱配置."""
    account = _get_account_or_404(account_id, db, current_user)
    update_data = request.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_encrypted"] = encrypt(update_data.pop("password"))
    for key, value in update_data.items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account


@router.delete("/accounts/{account_id}")
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除邮箱配置."""
    account = _get_account_or_404(account_id, db, current_user)
    db.delete(account)
    db.commit()
    return {"message": "删除成功"}


# ── 邮件操作 ─────────────────────────────────────────────────


@router.get("/accounts/{account_id}/unread")
def get_unread_count(
    account_id: int,
    folder: str = Query("INBOX", description="邮箱文件夹"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取未读邮件数量."""
    account = _get_account_or_404(account_id, db, current_user)
    count = (
        db.query(EmailMessage)
        .filter(
            EmailMessage.account_id == account_id,
            EmailMessage.folder == folder,
            EmailMessage.is_read == False,
        )
        .count()
    )
    return {"account_id": account_id, "folder": folder, "unread_count": count}


@router.get("/accounts/{account_id}/messages", response_model=EmailMessageListResponse)
def list_messages(
    account_id: int,
    folder: str = Query("INBOX", description="邮箱文件夹"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取邮件列表."""
    account = _get_account_or_404(account_id, db, current_user)
    query = (
        db.query(EmailMessage)
        .filter(
            EmailMessage.account_id == account_id,
            EmailMessage.folder == folder,
        )
    )
    total = query.count()
    items = (
        query.order_by(EmailMessage.received_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return EmailMessageListResponse(total=total, items=items)


@router.put("/messages/{message_id}/read")
def mark_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """标记邮件为已读."""
    message = db.query(EmailMessage).filter(EmailMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="邮件不存在")
    message.is_read = True
    db.commit()
    return {"message": "标记成功"}


@router.put("/messages/{message_id}/star")
def toggle_star(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """切换邮件星标状态."""
    message = db.query(EmailMessage).filter(EmailMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="邮件不存在")
    message.is_starred = not message.is_starred
    db.commit()
    return {"message": "操作成功", "is_starred": message.is_starred}


# ── 发送邮件 ─────────────────────────────────────────────────


@router.post("/accounts/{account_id}/send")
def send_email(
    account_id: int,
    request: SendEmailRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """发送邮件."""
    account = _get_account_or_404(account_id, db, current_user)
    password = decrypt(account.password_encrypted)

    with SmtpClient(account.smtp_server, account.smtp_port, account.smtp_ssl) as client:
        try:
            client.connect(account.username, password)
            result = client.send_email(
                from_addr=account.email,
                to_addrs=request.to,
                subject=request.subject,
                body=request.body if not request.html else None,
                html=request.body if request.html else None,
                cc=request.cc,
            )
        except Exception as e:
            logger.error(f"Send email failed: {e}")
            raise HTTPException(status_code=502, detail=f"发送失败: {str(e)}")

    if not result.get("success"):
        raise HTTPException(status_code=502, detail=result.get("message", "发送失败"))

    return {"message": "发送成功", "recipients": result.get("recipients")}


# ── 同步邮件 ─────────────────────────────────────────────────


@router.post("/accounts/{account_id}/sync")
def sync_emails(
    account_id: int,
    folder: str = Query("INBOX", description="邮箱文件夹"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """从 IMAP 服务器同步邮件到数据库."""
    account = _get_account_or_404(account_id, db, current_user)
    password = decrypt(account.password_encrypted)

    with ImapClient(account.imap_server, account.imap_port, account.imap_ssl) as client:
        try:
            client.connect(account.username, password)
            emails = client.fetch_emails(folder=folder, limit=limit)
        except Exception as e:
            logger.error(f"Sync emails failed: {e}")
            raise HTTPException(status_code=502, detail=f"同步失败: {str(e)}")

    created = 0
    for mail_data in emails:
        # 按 message_id 去重
        msg_id = mail_data.get("message_id")
        if msg_id:
            existing = (
                db.query(EmailMessage)
                .filter(
                    EmailMessage.account_id == account_id,
                    EmailMessage.message_id == msg_id,
                )
                .first()
            )
            if existing:
                continue

        message = EmailMessage(
            account_id=account_id,
            message_id=mail_data.get("message_id"),
            uid=mail_data.get("uid"),
            subject=mail_data.get("subject"),
            sender=mail_data.get("sender"),
            recipients=mail_data.get("recipients"),
            cc=mail_data.get("cc"),
            body_text=mail_data.get("body_text"),
            body_html=mail_data.get("body_html"),
            has_attachment=mail_data.get("has_attachment", False),
            is_read=mail_data.get("is_read", False),
            is_starred=mail_data.get("is_starred", False),
            folder=mail_data.get("folder", folder),
            received_at=mail_data.get("received_at"),
        )
        db.add(message)
        created += 1

    db.commit()
    return {
        "message": "同步完成",
        "synced": len(emails),
        "created": created,
        "folder": folder,
    }
