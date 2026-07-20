"""Dashboard aggregation API – summarizes tasks, cron, reading, and email data."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.cron_execution import CronExecution, ExecutionStatus
from app.models.book import Book, BookStatus
from app.models.email_account import EmailAccount
from app.models.email_message import EmailMessage
from app.models.task_log import TaskLog

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("")
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregated dashboard data."""
    uid = current_user.id

    # ── Task statistics ──────────────────────────────────────────────────
    total_tasks = db.query(Task).filter(Task.user_id == uid).count()
    pending_tasks = db.query(Task).filter(
        Task.user_id == uid, Task.status == TaskStatus.PENDING
    ).count()
    in_progress_tasks = db.query(Task).filter(
        Task.user_id == uid, Task.status == TaskStatus.IN_PROGRESS
    ).count()
    completed_tasks = db.query(Task).filter(
        Task.user_id == uid, Task.status == TaskStatus.COMPLETED
    ).count()

    today = date.today()
    completed_today = db.query(Task).filter(
        Task.user_id == uid,
        Task.status == TaskStatus.COMPLETED,
        func.date(Task.updated_at) == today,
    ).count()

    overdue_tasks = db.query(Task).filter(
        Task.user_id == uid,
        Task.due_date < today,
        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS]),
    ).count()

    # ── Cron / execution statistics ──────────────────────────────────────
    total_cron = db.query(CronExecution).count()
    success_count = db.query(CronExecution).filter(
        CronExecution.status == ExecutionStatus.SUCCESS
    ).count()
    failed_count = db.query(CronExecution).filter(
        CronExecution.status == ExecutionStatus.FAILED
    ).count()
    running_count = db.query(CronExecution).filter(
        CronExecution.status == ExecutionStatus.RUNNING
    ).count()
    success_rate = round((success_count / total_cron * 100), 1) if total_cron > 0 else 0.0

    # ── Reading statistics ───────────────────────────────────────────────
    total_books = db.query(Book).filter(Book.user_id == uid).count()
    want_to_read = db.query(Book).filter(
        Book.user_id == uid, Book.status == BookStatus.WANT_TO_READ
    ).count()
    reading_books = db.query(Book).filter(
        Book.user_id == uid, Book.status == BookStatus.READING
    ).count()
    finished_books = db.query(Book).filter(
        Book.user_id == uid, Book.status == BookStatus.FINISHED
    ).count()
    avg_progress = db.query(func.avg(Book.progress)).filter(
        Book.user_id == uid
    ).scalar() or 0
    avg_progress = round(float(avg_progress), 1)

    # 在读书籍列表
    reading_books_list = (
        db.query(Book)
        .filter(Book.user_id == uid, Book.status == BookStatus.READING)
        .order_by(Book.last_read_at.desc())
        .limit(10)
        .all()
    )

    # ── Email statistics ─────────────────────────────────────────────────
    total_accounts = db.query(EmailAccount).filter(EmailAccount.is_active == True).count()
    unread_count = db.query(EmailMessage).filter(
        EmailMessage.is_read == False
    ).count()

    # 未读邮件列表
    email_unread_list = (
        db.query(EmailMessage)
        .filter(EmailMessage.is_read == False)
        .order_by(EmailMessage.received_at.desc())
        .limit(5)
        .all()
    )

    # ── Recent items ─────────────────────────────────────────────────────
    recent_tasks = (
        db.query(Task)
        .filter(Task.user_id == uid)
        .order_by(Task.updated_at.desc())
        .limit(5)
        .all()
    )

    # ── Recent task logs ──────────────────────────────────────────────
    recent_logs = (
        db.query(TaskLog)
        .order_by(TaskLog.created_at.desc())
        .limit(5)
        .all()
    )

    # ── Build response ───────────────────────────────────────────────────
    return {
        "tasks": {
            "total": total_tasks,
            "pending": pending_tasks,
            "in_progress": in_progress_tasks,
            "completed": completed_tasks,
            "completed_today": completed_today,
            "overdue": overdue_tasks,
        },
        "cron": {
            "total_jobs": total_cron,
            "success_count": success_count,
            "failed_count": failed_count,
            "running_count": running_count,
            "success_rate": success_rate,
        },
        "reading": {
            "total_books": total_books,
            "want_to_read": want_to_read,
            "reading": reading_books,
            "finished": finished_books,
            "avg_progress": avg_progress,
        },
        "email": {
            "total_accounts": total_accounts,
            "unread_count": unread_count,
        },
        "reading_books": [
            {
                "id": b.id,
                "title": b.title,
                "author": b.author,
                "progress": b.progress,
                "cover_url": b.cover_url,
            }
            for b in reading_books_list
        ],
        "email_unread": [
            {
                "id": e.id,
                "subject": e.subject,
                "sender": e.sender,
                "received_at": e.received_at.isoformat() if e.received_at else None,
            }
            for e in email_unread_list
        ],
        "recent_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "type": t.type,
                "status": t.status,
                "priority": t.priority,
                "due_date": str(t.due_date) if t.due_date else None,
            }
            for t in recent_tasks
        ],
        "recent_logs": [
            {
                "id": l.id,
                "task_id": l.task_id,
                "content": l.content,
                "log_type": l.log_type,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in recent_logs
        ],
    }


@router.get("/heatmap")
def get_heatmap(
    days: int = Query(365, ge=30, le=730),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取任务完成热力图数据"""
    uid = current_user.id
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # 按日期分组统计已完成任务数量（单次查询）
    results = (
        db.query(
            cast(Task.updated_at, Date).label("date"),
            func.count(Task.id).label("count"),
        )
        .filter(
            Task.user_id == uid,
            Task.status == TaskStatus.COMPLETED,
            cast(Task.updated_at, Date) >= start_date,
            cast(Task.updated_at, Date) <= end_date,
        )
        .group_by(cast(Task.updated_at, Date))
        .all()
    )

    heatmap = {str(row.date): row.count for row in results}

    return {
        "start_date": str(start_date),
        "end_date": str(end_date),
        "data": heatmap,
    }
