"""Hermes Cron API client – wraps the Hermes /api/cron endpoints."""

import httpx
from typing import Optional

from app.core.config import settings


class HermesClient:
    def __init__(self):
        self.base_url = settings.HERMES_API_URL.rstrip("/")
        self.api_key = settings.HERMES_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def list_jobs(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/cron/jobs", headers=self.headers, timeout=15
            )
            resp.raise_for_status()
            return resp.json()

    async def get_job(self, job_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/api/cron/jobs/{job_id}", headers=self.headers, timeout=15
            )
            resp.raise_for_status()
            return resp.json()

    async def run_job(self, job_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/cron/jobs/{job_id}/run", headers=self.headers, timeout=30
            )
            resp.raise_for_status()
            return resp.json()

    async def pause_job(self, job_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/cron/jobs/{job_id}/pause", headers=self.headers, timeout=15
            )
            resp.raise_for_status()
            return resp.json()

    async def resume_job(self, job_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/api/cron/jobs/{job_id}/resume", headers=self.headers, timeout=15
            )
            resp.raise_for_status()
            return resp.json()


hermes_client = HermesClient()
