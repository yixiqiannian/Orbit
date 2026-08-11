import requests

BASE = "http://localhost:8000"

# Login
resp = requests.post(f"{BASE}/api/auth/login", json={"username": "admin", "password": "orbit2026"})
data = resp.json()
token = data["access_token"]
print(f"Token obtained (len={len(token)})")

# Sync
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
resp2 = requests.post(f"{BASE}/api/reading/sync", headers=headers)
print(f"Status: {resp2.status_code}")
print(f"Body: {resp2.text}")
