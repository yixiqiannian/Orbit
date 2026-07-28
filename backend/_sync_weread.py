import requests
import sys
from datetime import datetime, timedelta

ORBIT_URL = "http://localhost:8000"

# 生成 JWT token
try:
    from jose import jwt
    JWT_SECRET = "orbit-secret-key-2026-change-this"
    payload = {"sub": "1", "exp": datetime.utcnow() + timedelta(hours=2)}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    print("[OK] Token generated via JWT_SECRET")
except Exception as e:
    print(f"[ERROR] JWT generation failed: {e}")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 执行同步
print("[INFO] Calling POST /api/reading/sync ...")
try:
    resp = requests.post(f"{ORBIT_URL}/api/reading/sync", headers=headers, timeout=120)
    print(f"[HTTP] Status: {resp.status_code}")
    data = resp.json()
    print(f"[RESULT] {data}")
except Exception as e:
    print(f"[ERROR] Sync failed: {e}")
    sys.exit(1)

# 验证结果
print("\n[VERIFY] Checking books ...")
try:
    resp = requests.get(f"{ORBIT_URL}/api/reading/books", headers=headers, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        total = data.get('total', '?')
        items = data.get('items', [])
        print(f"[VERIFY] Total books in Orbit: {total}")
        status_count = {}
        for book in items:
            s = book.get("status", "unknown")
            status_count[s] = status_count.get(s, 0) + 1
        for s, c in status_count.items():
            print(f"  {s}: {c}")
    else:
        print(f"[WARN] Verify returned {resp.status_code}: {resp.text[:200]}")
except Exception as e:
    print(f"[WARN] Verification failed: {e}")

print("\n[DONE] Sync complete.")
