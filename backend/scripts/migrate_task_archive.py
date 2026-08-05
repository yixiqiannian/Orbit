"""Migration script to add archive columns to tasks table."""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from sqlalchemy import text


def migrate():
    db = SessionLocal()
    try:
        # 检查 tasks 表是否有 archived 列
        result = db.execute(text("SHOW COLUMNS FROM tasks LIKE 'archived'"))
        if not result.fetchone():
            print("Adding archived column to tasks table...")
            db.execute(text("ALTER TABLE tasks ADD COLUMN archived BOOLEAN NOT NULL DEFAULT FALSE"))
            db.commit()
            print("  - archived added")
        else:
            print("  - archived already exists")

        # 检查 tasks 表是否有 archived_month 列
        result = db.execute(text("SHOW COLUMNS FROM tasks LIKE 'archived_month'"))
        if not result.fetchone():
            print("Adding archived_month column to tasks table...")
            db.execute(text("ALTER TABLE tasks ADD COLUMN archived_month VARCHAR(7) NULL"))
            db.commit()
            print("  - archived_month added")
        else:
            print("  - archived_month already exists")

        # 为已有任务设置 archived 默认值
        db.execute(text("UPDATE tasks SET archived = FALSE WHERE archived IS NULL"))
        db.commit()
        print("  - existing tasks archived field set to FALSE")

        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
