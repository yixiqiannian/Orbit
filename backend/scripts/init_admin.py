"""Initialize the default admin user."""

import sys
import os

# Add project root to path so app imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def init_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("orbit2026"),
                email="admin@orbit.local",
            )
            db.add(admin)
            db.commit()
            print("Admin user created: admin / orbit2026")
        else:
            print("Admin user already exists")
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
