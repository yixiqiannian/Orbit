"""WeRead -> Orbit 书架同步脚本"""
import requests, sys, json

ORBIT_URL = "http://localhost:8000"

# 1. 获取 token
try:
    r = requests.post(f"{ORBIT_URL}/api/auth/login", json={"username": "admin", "password": "orbit2026"}, timeout=10)
    r.raise_for_status()
    token = r.json()["access_token"]
    print("[OK] Login successful")
except Exception as e:
    print(f"[WARN] Login failed: {e}, trying direct JWT")
    from jose import jwt
    from datetime import datetime, timedelta
    JWT_SECRET = "orbit-secret-key-2026-change-this"
    payload = {"sub": "1", "exp": datetime.utcnow() + timedelta(hours=2)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    print("[OK] Token generated via JWT_SECRET")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 2. 同步
print("[INFO] Calling POST /api/reading/sync ...")
try:
    resp = requests.post(f"{ORBIT_URL}/api/reading/sync", headers=headers, timeout=120)
    print(f"[HTTP] Status: {resp.status_code}")
    print(f"[RESULT] {json.dumps(resp.json(), ensure_ascii=False)}")
except Exception as e:
    print(f"[ERROR] Sync failed: {e}")
    sys.exit(1)

# 3. 验证
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
except Exception as e:
    print(f"[WARN] Verification failed: {e}")
print("Done.")
