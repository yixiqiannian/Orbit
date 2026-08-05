"""WeRead → Orbit 直连数据库同步脚本"""
import sys
import time
import httpx
import pymysql
from datetime import datetime

# ── WeRead API ──
WEREAD_API_KEY = "wrk-5DBk3Kd4RtiRuLlaVbvKFgAA"
WEREAD_BASE_URL = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION = "1.0.4"

# ── MySQL ──
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Qq564725728.",
    "database": "orbit",
    "charset": "utf8mb4",
}

USER_ID = 1


def weread_request(api_name: str, **kwargs) -> dict:
    headers = {
        "Authorization": f"Bearer {WEREAD_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {"api_name": api_name, "skill_version": SKILL_VERSION, **kwargs}
    resp = httpx.post(WEREAD_BASE_URL, headers=headers, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()


def upsert_book(conn, weread_id, title, author, cover, progress, last_read_at, finish_reading):
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
                """UPDATE books SET title=%s, author=%s, cover_url=%s, progress=%s,
                   status=%s, last_read_at=%s, updated_at=NOW() WHERE id=%s""",
                (title, author, cover, progress, status, last_read_at, row[0]),
            )
            return "updated"
        else:
            cur.execute(
                """INSERT INTO books
                   (user_id, weread_id, title, author, cover_url, progress, status, last_read_at, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (USER_ID, weread_id, title, author, cover, progress, status, last_read_at),
            )
            return "inserted"


def main():
    print("=== WeRead → Orbit 直连同步 ===\n")

    # 1. Get shelf
    print("[1/3] 获取微信读书书架...")
    shelf = weread_request("/shelf/sync")
    books = shelf.get("books", [])
    albums = shelf.get("albums", [])
    mp = shelf.get("mp")
    total = len(books) + len(albums) + (1 if mp else 0)
    print(f"  书架: {len(books)} 电子书, {len(albums)} 专辑" + (", 有文章收藏" if mp else "") + f"  共 {total} 条")

    # 2. Connect DB
    print("[2/3] 连接数据库...")
    conn = pymysql.connect(**DB_CONFIG)

    # Check current count
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM books WHERE user_id=%s", (USER_ID,))
        existing = cur.fetchone()[0]
    print(f"  现有记录: {existing}")

    # 3. Sync books
    print("[3/3] 同步中...\n")
    inserted = updated = errors = 0

    for i, item in enumerate(books):
        weread_id = item.get("bookId")
        title = item.get("title", "")
        author = item.get("author", "")
        cover = item.get("cover", "")
        finish_reading = item.get("finishReading", 0)
        read_update_time = item.get("readUpdateTime")

        progress = 0
        last_read_at = None
        try:
            prog_data = weread_request("/book/getprogress", bookId=weread_id)
            book_prog = prog_data.get("book", {})
            progress = book_prog.get("progress", 0)
            update_time = book_prog.get("updateTime")
            if update_time:
                last_read_at = datetime.fromtimestamp(update_time)
        except Exception as e:
            if read_update_time:
                last_read_at = datetime.fromtimestamp(read_update_time)
            print(f"  [!] 进度获取失败: {title} - {e}")

        try:
            result = upsert_book(conn, weread_id, title, author, cover, progress, last_read_at, finish_reading)
            if result == "inserted":
                inserted += 1
            else:
                updated += 1

            icon = "+" if result == "inserted" else "✓"
            print(f"  [{i+1}/{len(books)}] {icon} {title} ({progress}%)")
        except Exception as e:
            errors += 1
            print(f"  [{i+1}/{len(books)}] ✗ {title} - {e}")

        if (i + 1) % 10 == 0:
            conn.commit()
            time.sleep(0.5)

    conn.commit()

    # Summary
    print(f"\n=== 完成 ===")
    print(f"  新增: {inserted}, 更新: {updated}, 失败: {errors}")

    with conn.cursor() as cur:
        cur.execute("SELECT status, COUNT(*) FROM books WHERE user_id=%s GROUP BY status", (USER_ID,))
        stats = cur.fetchall()
        labels = {"want_to_read": "想读", "reading": "在读", "finished": "已读"}
        print(f"\n=== Orbit 统计 ===")
        for status, count in stats:
            print(f"  {labels.get(status, status)}: {count}")
        print(f"  总计: {sum(c for _, c in stats)}")

    conn.close()


if __name__ == "__main__":
    main()
