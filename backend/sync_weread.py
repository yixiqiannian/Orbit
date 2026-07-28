import sys
sys.path.insert(0, '.')
import requests
from app.core.security import create_access_token

BASE = 'http://localhost:8000'

# Generate JWT token
token = create_access_token(data={'sub': '1'})
print(f"Token: {token[:20]}...")

# Sync
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
print("\n=== Sync WeRead Bookshelf ===")
try:
    sync = requests.post(f'{BASE}/api/reading/sync', headers=headers, timeout=120)
    print(f"Status: {sync.status_code}")
    print(f"Response: {sync.json()}")
except Exception as e:
    print(f"Error: {e}")

# Verify - get stats
print("\n=== Reading Stats ===")
try:
    stats = requests.get(f'{BASE}/api/reading/stats', headers=headers, timeout=30)
    print(f"Status: {stats.status_code}")
    print(f"Stats: {stats.json()}")
except Exception as e:
    print(f"Error: {e}")
