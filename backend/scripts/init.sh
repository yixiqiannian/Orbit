#!/bin/bash
# 等待 MySQL 启动
echo "Waiting for MySQL..."
sleep 10

# 初始化数据库表
echo "Initializing database..."
python scripts/init_db.py

# 初始化管理员账户
echo "Creating admin user..."
python scripts/init_admin.py

echo "Initialization complete!"
