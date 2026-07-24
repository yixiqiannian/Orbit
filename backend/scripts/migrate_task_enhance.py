"""Migration script to add new columns to tasks table and create new tables."""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, SessionLocal
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        # 检查 tasks 表是否有 category_id 列
        result = db.execute(text("SHOW COLUMNS FROM tasks LIKE 'category_id'"))
        if not result.fetchone():
            print("Adding category_id column to tasks table...")
            db.execute(text("ALTER TABLE tasks ADD COLUMN category_id INTEGER NULL"))
            db.execute(text("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_category FOREIGN KEY (category_id) REFERENCES task_categories(id)"))
            db.commit()
            print("  - category_id added")
        else:
            print("  - category_id already exists")

        # 检查 tasks 表是否有 project_id 列
        result = db.execute(text("SHOW COLUMNS FROM tasks LIKE 'project_id'"))
        if not result.fetchone():
            print("Adding project_id column to tasks table...")
            db.execute(text("ALTER TABLE tasks ADD COLUMN project_id INTEGER NULL"))
            db.execute(text("ALTER TABLE tasks ADD CONSTRAINT fk_tasks_project FOREIGN KEY (project_id) REFERENCES projects(id)"))
            db.commit()
            print("  - project_id added")
        else:
            print("  - project_id already exists")

        # 检查 priority 列类型，如果是 INTEGER 则改为 VARCHAR
        result = db.execute(text("SHOW COLUMNS FROM tasks WHERE Field = 'priority'"))
        col = result.fetchone()
        if col and 'int' in col[1].lower():
            print("Migrating priority column from INTEGER to VARCHAR...")
            # 先修改列类型（MySQL 会自动转换 0 -> '0'）
            db.execute(text("ALTER TABLE tasks MODIFY COLUMN priority VARCHAR(20) DEFAULT 'normal'"))
            db.commit()
            # 然后更新值
            db.execute(text("""
                UPDATE tasks SET priority = CASE 
                    WHEN priority = '0' THEN 'normal'
                    WHEN priority = '1' THEN 'high'
                    WHEN priority = '2' THEN 'urgent'
                    ELSE 'low'
                END
            """))
            db.commit()
            print("  - priority migrated to VARCHAR")
        else:
            print("  - priority is already VARCHAR or not found")

        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
