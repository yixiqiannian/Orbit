import requests, sys

try:
    # 1. Health check
    r = requests.get('http://localhost:8000/docs', timeout=5)
    if r.status_code != 200:
        print(f"Orbit backend unhealthy: {r.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"Orbit backend not reachable: {e}")
    sys.exit(1)

# 2. Login
try:
    login = requests.post('http://localhost:8000/api/auth/login',
        json={'username': 'admin', 'password': 'orbit2026'}, timeout=10)
    login.raise_for_status()
    token = login.json()['access_token']
    print(f"Login OK")
except Exception as e:
    print(f"Login failed: {e}")
    sys.exit(1)

# 3. Sync
try:
    resp = requests.post('http://localhost:8000/api/reading/sync',
        headers={'Authorization': f'Bearer {token}'},
        json={}, timeout=120)
    print(f"Sync response ({resp.status_code}): {resp.text}")
except Exception as e:
    print(f"Sync failed: {e}")
    sys.exit(1)
