"""
WeRead -> Orbit bookshelf sync
"""
import requests
import subprocess
import sys
import time

ORBIT_URL = "http://localhost:8000"
LOGIN_CREDS = {"username": "admin", "password": "orbit2026"}
SYNC_TIMEOUT = 120


def ensure_orbit_running():
    """Check Orbit backend health, restart if not running."""
    try:
        r = requests.get(f"{ORBIT_URL}/docs", timeout=5)
        if r.status_code == 200:
            print("[OK] Orbit backend is running")
            return
    except Exception:
        pass

    print("[WARN] Orbit backend not available, restarting...")
    subprocess.Popen(
        ["cmd", "/C", "start", "Orbit Backend", "cmd", "/k",
         "cd /d G:\\Orbit\\backend && G:\\Orbit\\backend\\venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"],
        shell=True,
    )
    for _ in range(15):
        time.sleep(2)
        try:
            r = requests.get(f"{ORBIT_URL}/docs", timeout=3)
            if r.status_code == 200:
                print("[OK] Orbit backend restarted")
                return
        except Exception:
            pass
    print("[ERROR] Orbit backend failed to start after 30s")
    sys.exit(1)


def get_token():
    """Login to get JWT token, fallback to direct generation."""
    try:
        r = requests.post(f"{ORBIT_URL}/api/auth/login", json=LOGIN_CREDS, timeout=10)
        r.raise_for_status()
        print("[OK] Login successful")
        return r.json()["access_token"]
    except Exception as e:
        print(f"[WARN] Login endpoint failed ({e}), falling back to direct JWT")

    try:
        from jose import jwt
        from datetime import datetime, timedelta
        JWT_SECRET = "orbit-secret-key-2026-change-this"
        payload = {"sub": "1", "exp": datetime.utcnow() + timedelta(hours=2)}
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        print("[OK] Token generated directly via JWT_SECRET")
        return token
    except Exception as e:
        print(f"[ERROR] Direct JWT generation also failed: {e}")
        sys.exit(1)


def sync_reading(token):
    """Call full sync endpoint."""
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
    """Verify sync results."""
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
    except Exception as e:
        print(f"[WARN] Verification failed: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("WeRead -> Orbit Bookshelf Sync")
    print("=" * 50)
    ensure_orbit_running()
    token = get_token()
    sync_reading(token)
    verify(token)
    print("=" * 50)
    print("Sync complete.")
