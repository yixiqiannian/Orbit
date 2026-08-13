"""GitHub Trending 抓取服务."""

import re

import httpx
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending?since=daily"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _parse_num(text: str) -> int:
    """'11,519' -> 11519; '2,855' -> 2855; '-' -> 0"""
    t = text.strip().replace(",", "")
    if not t or t == "-":
        return 0
    try:
        return int(t)
    except ValueError:
        return 0


def _parse_today_stars(f6_text: str) -> int:
    """'HTML 11,519 728 Built by 2,855 stars today' -> 2855"""
    m = re.search(r"Built by\s+([\d,]+)\s+stars today", f6_text)
    return _parse_num(m.group(1)) if m else 0


def parse_trending(html: str) -> list[dict]:
    """解析 GitHub Trending 页面 HTML，返回条目 dict 列表。"""
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for i, row in enumerate(soup.select("article.Box-row"), start=1):
        a = row.select_one("h2 a.Link")
        if not a:
            continue
        href = a.get("href", "")            # /owner/repo
        title = a.get_text(" ", strip=True)  # "owner / repo"
        desc_el = row.select_one("p")
        lang_el = row.select_one('span[itemprop="programmingLanguage"]')
        stars_el = row.select_one('a[href*="stargazers"]')
        forks_el = row.select_one('a[href*="forks"]')
        f6 = row.select_one(".f6")
        items.append({
            "rank": i,
            "title": title.replace(" / ", "/").strip(),
            "url": f"https://github.com{href}",
            "description": desc_el.get_text(strip=True) if desc_el else None,
            "language": lang_el.get_text(strip=True) if lang_el else None,
            "stars_total": _parse_num(stars_el.get_text()) if stars_el else 0,
            "forks": _parse_num(forks_el.get_text()) if forks_el else 0,
            "stars_today": _parse_today_stars(f6.get_text(" ", strip=True)) if f6 else 0,
        })
    return items


async def fetch_trending() -> list[dict]:
    """抓取并解析 GitHub Trending（每日）。失败时抛 httpx.HTTPError。"""
    async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(TRENDING_URL)
        resp.raise_for_status()
        return parse_trending(resp.text)
