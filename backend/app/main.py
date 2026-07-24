from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

from app.api.auth import router as auth_router
from app.api.cron import router as cron_router
from app.api.reading import router as reading_router
from app.api.tasks import router as tasks_router
from app.api.dashboard import router as dashboard_router
from app.api.email import router as email_router
from app.api.nav import router as nav_router
from app.api.knowledge import router as knowledge_router
from app.api.task_logs import router as task_logs_router
from app.api.projects import router as projects_router
from app.api.task_categories import router as task_categories_router

app = FastAPI(title="Orbit API", version="1.0.0")

# CORS 配置 - 开发模式允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Error: {exc}")
    print(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Routers
app.include_router(auth_router)
app.include_router(cron_router)
app.include_router(reading_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)
app.include_router(email_router)
app.include_router(nav_router)
app.include_router(knowledge_router)
app.include_router(task_logs_router)
app.include_router(projects_router)
app.include_router(task_categories_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
