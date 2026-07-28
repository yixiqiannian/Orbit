import sys
sys.path.insert(0, '.')
import requests
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token

db = SessionLocal()
users = db.query(User).all()
if users:
    token = create_access_token(data={"sub": str(users[0].id)})
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post("http://localhost:8000/api/reading/sync", headers=headers)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")
else:
    print("No users found")
db.close()
