"""WeRead (微信读书) API client."""

import httpx
from typing import Optional
from app.core.config import settings


class WeReadClient:
    BASE_URL = "https://i.weread.qq.com/api/agent/gateway"
    SKILL_VERSION = "1.0.4"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def _request(self, api_name: str, **kwargs) -> dict:
        body = {"api_name": api_name, "skill_version": self.SKILL_VERSION, **kwargs}
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.BASE_URL, headers=self.headers, json=body, timeout=30)
            resp.raise_for_status()
            return resp.json()

    async def get_shelf(self) -> dict:
        """获取书架数据."""
        return await self._request("/shelf/sync")

    async def search_books(self, keyword: str, count: int = 10) -> dict:
        """搜索书籍."""
        return await self._request("/store/search", keyword=keyword, count=count)

    async def get_book_info(self, book_id: str) -> dict:
        """获取书籍详情."""
        return await self._request("/book/info", bookId=book_id)

    async def get_book_progress(self, book_id: str) -> dict:
        """获取阅读进度."""
        return await self._request("/book/getprogress", bookId=book_id)

    async def get_chapter_info(self, book_id: str) -> dict:
        """获取章节目录."""
        return await self._request("/book/chapterinfo", bookId=book_id)

    async def get_read_data(self, book_id: str) -> dict:
        """获取阅读数据."""
        return await self._request("/book/readdata", bookId=book_id)


def get_weread_client() -> Optional[WeReadClient]:
    """获取微信读书客户端实例."""
    api_key = settings.WEREAD_API_KEY
    if not api_key:
        return None
    return WeReadClient(api_key)
