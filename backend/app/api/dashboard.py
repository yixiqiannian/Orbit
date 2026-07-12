"""Dashboard aggregation API – summarizes tasks, cron, and reading data."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.task import Task, TaskStatus
from app.models.cron_execution import CronExecution, ExecutionStatus
from app.models.book import Book, BookStatus
from app.schemas.dashboard import (
    DashboardResponse,
    TaskSummary,
    CronSummary,
    ReadingSummary,
    RecentTask,
    RecentExecution,
)

router = APIRouter(prefix="/api/dashboard", tags=["仪表盘"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return aggregated dashboard data: task stats, cron stats, reading stats,
    plus the 5 most-recent tasks and 5 most-recent cron executions."""
    uid = current_user.id

    # ── Task statistics ──────────────────────────────────────────────────
    total_tasks = db.query(Task).filter(Task.user_id == uid).count()
    pending_tasks = db.query(Task).filter(
        Task.user_id == uid, Task.status == TaskStatus.PENDING
    ).count()
    in_progress_tasks = db.query(Task).filter(
        Task.user_id == uid, Task.status == TaskStatus.IN_PROGRESS
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
    # CronExecution has no "enabled" field; treat all recorded jobs as enabled
    enabled_cron = total_cron

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_executions_count = db.query(CronExecution).filter(
        CronExecution.executed_at >= seven_days_ago
    ).count()

    success_count = db.query(CronExecution).filter(
        CronExecution.status == ExecutionStatus.SUCCESS
    ).count()
    success_rate = round((success_count / total_cron * 100), 1) if total_cron > 0 else 0.0

    # ── Reading statistics ───────────────────────────────────────────────
    total_books = db.query(Book).filter(Book.user_id == uid).count()
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

    # ── Recent items ─────────────────────────────────────────────────────
    recent_tasks = (
        db.query(Task)
        .filter(Task.user_id == uid)
        .order_by(Task.updated_at.desc())
        .limit(5)
        .all()
    )

    recent_exec_list = (
        db.query(CronExecution)
        .order_by(CronExecution.executed_at.desc())
        .limit(5)
        .all()
    )

    # ── Build response ───────────────────────────────────────────────────
    return DashboardResponse(
        tasks=TaskSummary(
            total=total_tasks,
            pending=pending_tasks,
            in_progress=in_progress_tasks,
            completed_today=completed_today,
            overdue=overdue_tasks,
        ),
        cron=CronSummary(
            total_jobs=total_cron,
            enabled=enabled_cron,
            recent_executions=recent_executions_count,
            success_rate=success_rate,
        ),
        reading=ReadingSummary(
            total_books=total_books,
            reading=reading_books,
            finished=finished_books,
            avg_progress=avg_progress,
        ),
        recent_tasks=[
            RecentTask(
                id=t.id,
                title=t.title,
                type=t.type,
                status=t.status,
                priority=t.priority,
                due_date=str(t.due_date) if t.due_date else None,
                updated_at=t.updated_at,
            )
            for t in recent_tasks
        ],
        recent_executions=[
            RecentExecution(
                id=e.id,
                cron_job_id=e.cron_job_id,
                cron_job_name=e.cron_job_name,
                status=e.status,
                executed_at=e.executed_at,
            )
            for e in recent_exec_list
        ],
    )
