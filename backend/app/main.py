from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.cron import router as cron_router
from app.api.reading import router as reading_router
from app.api.tasks import router as tasks_router
from app.api.dashboard import router as dashboard_router

app = FastAPI(title="Orbit API", version="1.0.0")

# CORS 配置 - 允许 localhost 和 127.0.0.1
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(cron_router)
app.include_router(reading_router)
app.include_router(tasks_router)
app.include_router(dashboard_router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
