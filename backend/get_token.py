import sys
sys.path.insert(0, '.')
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token

db = SessionLocal()
users = db.query(User).all()
if users:
    token = create_access_token(data={"sub": str(users[0].id)})
    with open('token.txt', 'w') as f:
        f.write(token)
    print('Token written to token.txt')
db.close()
