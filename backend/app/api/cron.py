"""Scheduled-task (Cron) API – reads from Hermes cron jobs."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import subprocess
import json

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.cron_execution import CronExecution, ExecutionStatus

router = APIRouter(prefix="/api/cron", tags=["定时任务"])


def get_hermes_cron_jobs() -> list[dict]:
    """从 Hermes 获取定时任务列表."""
    try:
        result = subprocess.run(
            ["hermes", "cron", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception:
        pass
    
    # 如果 --json 不支持，尝试解析文本输出
    try:
        result = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # 解析文本格式
            jobs = []
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if '│' in line:
                    parts = [p.strip() for p in line.split('│') if p.strip()]
                    if len(parts) >= 4:
                        jobs.append({
                            "id": parts[0],
                            "name": parts[1],
                            "schedule": parts[2],
                            "enabled": "enabled" in line.lower() or "✓" in line,
                            "last_run": parts[3] if len(parts) > 3 else None,
                            "status": parts[4] if len(parts) > 4 else None,
                        })
            return jobs
    except Exception:
        pass
    
    return []


@router.get("/jobs")
async def list_jobs(current_user: User = Depends(get_current_user)):
    """获取定时任务列表."""
    try:
        # 使用 cronjob 工具获取任务列表
        result = subprocess.run(
            ["python", "-c", """
import json
from hermes_tools import terminal
result = terminal("hermes cron list")
print(result.get("output", ""))
"""],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="G:\\Hermes"
        )
        
        # 解析输出
        jobs = []
        if result.returncode == 0:
            output = result.stdout
            lines = output.strip().split('\n')
            current_job = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_job:
                        jobs.append(current_job)
                        current_job = {}
                    continue
                
                # 解析任务信息
                if '│' in line:
                    parts = [p.strip() for p in line.split('│') if p.strip()]
                    if len(parts) >= 3:
                        current_job = {
                            "id": parts[0],
                            "name": parts[1],
                            "schedule": parts[2],
                            "enabled": True,
                            "last_run": parts[3] if len(parts) > 3 else None,
                            "status": parts[4] if len(parts) > 4 else None,
                        }
            
            if current_job:
                jobs.append(current_job)
        
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {e}")


@router.get("/jobs/list")
async def list_jobs_simple(current_user: User = Depends(get_current_user)):
    """获取定时任务列表（简化版）."""
    # 静态任务列表，实际应该从 Hermes 读取
    return [
        {
            "id": "moon-blog-k8s-tutorial",
            "name": "K8s 教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:09:14",
            "status": "ok"
        },
        {
            "id": "moon-blog-docker-tutorial",
            "name": "Docker 教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:13:08",
            "status": "ok"
        },
        {
            "id": "moon-blog-linux-tutorial",
            "name": "Linux 教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:16:45",
            "status": "ok"
        },
        {
            "id": "moon-blog-mysql-tutorial",
            "name": "MySQL 教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:32:51",
            "status": "error"
        },
        {
            "id": "moon-blog-pgsql-tutorial",
            "name": "PostgreSQL 教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:40:26",
            "status": "ok"
        },
        {
            "id": "moon-blog-redis-tutorial",
            "name": "Redis 教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:43:33",
            "status": "ok"
        },
        {
            "id": "moon-blog-nginx-tutorial",
            "name": "Nginx 教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:44:56",
            "status": "ok"
        },
        {
            "id": "moon-blog-daily-summary",
            "name": "每日总结",
            "schedule": "0 22 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:19:37",
            "status": "ok"
        },
        {
            "id": "moon-blog-obsidian-sync",
            "name": "Obsidian 同步",
            "schedule": "30 20 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:37:52",
            "status": "ok"
        },
        {
            "id": "moon-blog-ima-sync",
            "name": "IMA 知识库同步",
            "schedule": "0 21 * * *",
            "enabled": True,
            "last_run": "2026-07-13 02:21:04",
            "status": "ok"
        },
        {
            "id": "每日教程发布",
            "name": "公众号教程发布",
            "schedule": "0 20 * * *",
            "enabled": True,
            "last_run": None,
            "status": None
        },
        {
            "id": "Obsidian 同步",
            "name": "Obsidian 笔记同步",
            "schedule": "30 20 * * *",
            "enabled": True,
            "last_run": None,
            "status": None
        },
        {
            "id": "IMA 知识库同步",
            "name": "IMA 知识库同步",
            "schedule": "0 21 * * *",
            "enabled": True,
            "last_run": None,
            "status": None
        },
        {
            "id": "每日总结",
            "name": "每日工作总结",
            "schedule": "0 22 * * *",
            "enabled": True,
            "last_run": None,
            "status": None
        },
        {
            "id": "每日科技/AI热点",
            "name": "科技热点",
            "schedule": "0 9 * * *",
            "enabled": False,
            "last_run": "2026-07-07 18:29:12",
            "status": "error"
        },
        {
            "id": "每周科技/AI热点",
            "name": "科技周报",
            "schedule": "0 9 * * 1",
            "enabled": False,
            "last_run": "2026-07-07 18:29:12",
            "status": "error"
        }
    ]


@router.get("/executions")
def list_executions(
    job_id: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取执行记录."""
    query = db.query(CronExecution)
    if job_id:
        query = query.filter(CronExecution.cron_job_id == job_id)
    return query.order_by(CronExecution.executed_at.desc()).limit(50).all()


@router.post("/jobs/{job_id}/run")
async def run_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """执行定时任务."""
    try:
        # 调用 hermes cron run
        result = subprocess.run(
            ["hermes", "cron", "run", job_id],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 记录执行
        execution = CronExecution(
            cron_job_id=job_id,
            status=ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED,
            result=result.stdout if result.returncode == 0 else None,
            error_message=result.stderr if result.returncode != 0 else None,
        )
        db.add(execution)
        db.commit()
        
        if result.returncode == 0:
            return {"success": True, "message": "任务已触发执行"}
        else:
            return {"success": False, "message": f"执行失败: {result.stderr}"}
    except Exception as e:
        return {"success": False, "message": f"执行失败: {e}"}
