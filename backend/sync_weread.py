import requests

BASE = 'http://localhost:8000'

# Step 1: Login
try:
    login = requests.post(f'{BASE}/api/auth/login',
        json={'username': 'admin', 'password': 'orbit2026'}, timeout=10)
    login.raise_for_status()
    token = login.json()['access_token']
    print('Login OK')
except Exception as e:
    print(f'Login failed: {e}')
    exit(1)

# Step 2: Sync
try:
    sync = requests.post(f'{BASE}/api/reading/sync',
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        timeout=120)
    print(f'Sync: {sync.status_code} {sync.text}')
except Exception as e:
    print(f'Sync error: {e}')
    exit(1)

# Step 3: Verify
if sync.status_code == 200:
    try:
        books = requests.get(f'{BASE}/api/reading/books',
            headers={'Authorization': f'Bearer {token}'}, timeout=10)
        data = books.json()
        total = data.get('total', 'N/A')
        items = data.get('items', [])
        print(f'Total books: {total}')
        
        status_count = {}
        for b in items:
            status = b.get('status', 'unknown')
            status_count[status] = status_count.get(status, 0) + 1
        print(f'Status distribution: {status_count}')
        
        print('Sample books:')
        for i, b in enumerate(items[:5]):
            title = b.get('title', 'N/A')
            status = b.get('status', 'N/A')
            progress = b.get('progress', 'N/A')
            print(f'  {i+1}. [{status}] {title} (progress: {progress}%)')
        if len(items) > 5:
            print(f'  ... and {len(items) - 5} more')
    except Exception as e:
        print(f'Verify error: {e}')

print('Done')
