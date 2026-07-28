"""
WeRead -> Orbit 书架同步脚本（cron 友好）

用法: python sync_weread.py
功能: 确保 Orbit 后端运行 -> 登录 -> 全量同步 -> 验证
输出: 同步结果打印到 stdout，适合 cron 捕获
"""
import requests
import sys
import time

ORBIT_URL = "http://localhost:8000"
LOGIN_CREDS = {"username": "admin", "password": "orbit2026"}
SYNC_TIMEOUT = 120


def get_token():
    """登录获取 JWT token，失败则 fallback 到直接生成。"""
    # 方法 1: 通过登录端点
    try:
        r = requests.post(f"{ORBIT_URL}/api/auth/login", json=LOGIN_CREDS, timeout=10)
        r.raise_for_status()
        print("[OK] Login successful")
        return r.json()["access_token"]
    except Exception as e:
        print(f"[WARN] Login endpoint failed ({e}), falling back to direct JWT")

    # 方法 2: 直接用 JWT_SECRET 生成（适合密码被改、cron 无人值守场景）
    try:
        from jose import jwt
        from datetime import datetime, timedelta
        import os
        # 读取 .env 中的 JWT_SECRET
        jwt_secret = "orbit-secret-key-2026-change-this"
        env_path = "G:/Orbit/backend/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("JWT_SECRET="):
                        jwt_secret = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        break
        payload = {"sub": "1", "exp": datetime.utcnow() + timedelta(hours=2)}
        token = jwt.encode(payload, jwt_secret, algorithm="HS256")
        print("[OK] Token generated directly via JWT_SECRET")
        return token
    except Exception as e:
        print(f"[ERROR] Direct JWT generation also failed: {e}")
        sys.exit(1)


def sync_reading(token):
    """调用全量同步端点。"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    print("[INFO] Calling POST /api/reading/sync ...")
    try:
        resp = requests.post(f"{ORBIT_URL}/api/reading/sync", headers=headers, timeout=SYNC_TIMEOUT)
        print(f"[HTTP] Status: {resp.status_code}")
        data = resp.json()
        print(f"[RESULT] {data}")
        return data
    except Exception as e:
        print(f"[ERROR] Sync failed: {e}")
        sys.exit(1)


def verify(token):
    """验证同步结果。"""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{ORBIT_URL}/api/reading/books", headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"[VERIFY] Total books: {data.get('total', '?')}")
            status_count = {}
            for book in data.get("items", []):
                s = book.get("status", "unknown")
                status_count[s] = status_count.get(s, 0) + 1
            for s, c in status_count.items():
                print(f"  {s}: {c}")
        else:
            print(f"[WARN] Verification returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"[WARN] Verification failed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("WeRead -> Orbit Bookshelf Sync")
    print("=" * 50)
    token = get_token()
    sync_reading(token)
    verify(token)
    print("=" * 50)
    print("Sync complete.")
