"""Sync WeRead bookshelf to Orbit database."""
import sys
import time
import httpx
import pymysql
from datetime import datetime

# WeRead API
WEREAD_API_KEY = "wrk-5DBk3Kd4RtiRuLlaVbvKFgAA"
WEREAD_BASE_URL = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION = "1.0.4"

# MySQL
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Qq564725728.",
    "database": "orbit",
    "charset": "utf8mb4",
}

USER_ID = 1  # admin user


def weread_request(api_name: str, **kwargs) -> dict:
    headers = {
        "Authorization": f"Bearer {WEREAD_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {"api_name": api_name, "skill_version": SKILL_VERSION, **kwargs}
    resp = httpx.post(WEREAD_BASE_URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_shelf():
    return weread_request("/shelf/sync")


def get_progress(book_id: str) -> dict:
    return weread_request("/book/getprogress", bookId=book_id)


def upsert_book(conn, weread_id, title, author, cover, progress, last_read_at, finish_reading):
    """Insert or update a book in the database."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM books WHERE user_id=%s AND weread_id=%s", (USER_ID, weread_id))
        row = cur.fetchone()

        if progress >= 100 or finish_reading:
            status = "finished"
        elif progress > 0:
            status = "reading"
        else:
            status = "want_to_read"

        if row:
            cur.execute(
                """UPDATE books SET title=%s, author=%s, cover_url=%s, progress=%s, status=%s, last_read_at=%s, updated_at=NOW()
                   WHERE id=%s""",
                (title, author, cover, progress, status, last_read_at, row[0]),
            )
            return "updated"
        else:
            cur.execute(
                """INSERT INTO books (user_id, weread_id, title, author, cover_url, progress, status, last_read_at, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (USER_ID, weread_id, title, author, cover, progress, status, last_read_at),
            )
            return "inserted"


def main():
    print("=== WeRead → Orbit 书架同步 ===\n")

    # 1. Get shelf data
    print("1. 获取微信读书书架...")
    shelf = get_shelf()
    books = shelf.get("books", [])
    albums = shelf.get("albums", [])
    mp = shelf.get("mp")
    print(f"   书架: {len(books)} 本电子书, {len(albums)} 个专辑/有声书" + (", 有文章收藏" if mp else ""))
    print(f"   共 {len(books) + len(albums) + (1 if mp else 0)} 个条目\n")

    # 2. Connect to DB
    print("2. 连接数据库...")
    conn = pymysql.connect(**DB_CONFIG)
    print("   连接成功\n")

    # 3. Sync each book with progress
    print("3. 同步书籍数据...")
    inserted = 0
    updated = 0
    errors = 0

    for i, item in enumerate(books):
        weread_id = item.get("bookId")
        title = item.get("title", "")
        author = item.get("author", "")
        cover = item.get("cover", "")
        finish_reading = item.get("finishReading", 0)
        read_update_time = item.get("readUpdateTime")

        # Get reading progress
        progress = 0
        last_read_at = None
        try:
            prog_data = get_progress(weread_id)
            book_prog = prog_data.get("book", {})
            progress = book_prog.get("progress", 0)
            update_time = book_prog.get("updateTime")
            if update_time:
                last_read_at = datetime.fromtimestamp(update_time)
        except Exception as e:
            # Fallback to shelf's readUpdateTime
            if read_update_time:
                last_read_at = datetime.fromtimestamp(read_update_time)

        result = upsert_book(conn, weread_id, title, author, cover, progress, last_read_at, finish_reading)
        if result == "inserted":
            inserted += 1
        else:
            updated += 1

        status_icon = "✓" if result == "updated" else "+"
        prog_str = f"{progress}%"
        print(f"   [{i+1}/{len(books)}] {status_icon} {title} - {author or '未知'} ({prog_str})")

        # Rate limit: small delay to avoid hammering the API
        if (i + 1) % 10 == 0:
            time.sleep(0.5)

    conn.commit()

    # 4. Summary
    print(f"\n=== 同步完成 ===")
    print(f"   新增: {inserted} 本")
    print(f"   更新: {updated} 本")
    print(f"   失败: {errors} 本")
    print(f"   合计处理: {inserted + updated} 本")

    # 5. Show stats
    with conn.cursor() as cur:
        cur.execute("SELECT status, COUNT(*) FROM books WHERE user_id=%s GROUP BY status", (USER_ID,))
        stats = cur.fetchall()
        print(f"\n=== Orbit 阅读统计 ===")
        total = 0
        for status, count in stats:
            label = {"want_to_read": "想读", "reading": "在读", "finished": "已读"}.get(status, status)
            print(f"   {label}: {count} 本")
            total += count
        print(f"   总计: {total} 本")

    conn.close()


if __name__ == "__main__":
    main()
