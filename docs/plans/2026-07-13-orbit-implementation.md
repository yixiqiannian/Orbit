# Orbit - 个人管理系统 实现计划

> **For Hermes:** Use kanban-orchestrator to route tasks to backend-engineer, frontend-engineer, qa-engineer.

**Goal:** 构建一个模块化、可配置的个人后台管理系统，集成任务管理、定时任务、阅读规划、仪表盘。

**Architecture:**
- 前后端分离：Vue 3 + FastAPI
- 数据库：MySQL（可配置连接）
- 认证：JWT
- 部署：Docker Compose
- 定时任务：对接 Hermes Cron API

**Tech Stack:**
- Frontend: Vue 3 + Vite + Element Plus + Vue Router + Pinia
- Backend: Python 3.11 + FastAPI + SQLAlchemy + PyMySQL + JWT
- Database: MySQL 8.x
- Deploy: Docker Compose

---

## 模块设计

```
Orbit/
├── frontend/                 # Vue 3 前端
│   ├── src/
│   │   ├── api/             # API 请求封装
│   │   ├── components/      # 公共组件
│   │   ├── views/           # 页面
│   │   │   ├── Dashboard.vue    # 仪表盘
│   │   │   ├── Tasks.vue        # 任务管理
│   │   │   ├── CronJobs.vue     # 定时任务
│   │   │   ├── Reading.vue      # 阅读规划
│   │   │   └── Login.vue        # 登录
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── router/          # 路由配置
│   │   └── utils/           # 工具函数
│   └── Dockerfile
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/             # API 路由
│   │   │   ├── auth.py      # 认证接口
│   │   │   ├── tasks.py     # 任务接口
│   │   │   ├── cron.py      # 定时任务接口
│   │   │   ├── reading.py   # 阅读接口
│   │   │   └── dashboard.py # 仪表盘接口
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 数据模型
│   │   ├── services/        # 业务逻辑
│   │   ├── core/            # 核心配置
│   │   │   ├── config.py    # 可配置化设置
│   │   │   ├── security.py  # JWT 认证
│   │   │   └── database.py  # 数据库连接
│   │   └── utils/           # 工具函数
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml        # 编排配置
├── .env.example              # 环境变量示例
└── README.md                 # 部署文档
```

---

## 任务拆解（按依赖顺序）

### Phase 1: 项目初始化 + 数据库设计

| Task | Assignee | 描述 |
|------|----------|------|
| T1 | backend-engineer | 初始化后端项目结构 + FastAPI 框架 + 可配置化 |
| T2 | backend-engineer | 设计数据库表结构 + SQLAlchemy 模型 |
| T3 | frontend-engineer | 初始化 Vue 3 项目 + 路由 + Element Plus |

### Phase 2: 核心模块实现

| Task | Assignee | 依赖 | 描述 |
|------|----------|------|------|
| T4 | backend-engineer | T1 | 用户认证模块（登录/JWT） |
| T5 | backend-engineer | T2 | 任务管理 API（CRUD + 每日/规划/目标） |
| T6 | backend-engineer | T1 | 定时任务模块（对接 Hermes Cron） |
| T7 | backend-engineer | T2 | 阅读规划模块（书架/进度/状态） |
| T8 | backend-engineer | T5,T6,T7 | 仪表盘聚合 API |

### Phase 3: 前端页面实现

| Task | Assignee | 依赖 | 描述 |
|------|----------|------|------|
| T9 | frontend-engineer | T3 | 登录页面 |
| T10 | frontend-engineer | T3,T8 | 仪表盘首页 |
| T11 | frontend-engineer | T3,T5 | 任务管理页面 |
| T12 | frontend-engineer | T3,T6 | 定时任务页面 |
| T13 | frontend-engineer | T3,T7 | 阅读规划页面 |

### Phase 4: 集成测试 + 部署

| Task | Assignee | 依赖 | 描述 |
|------|----------|------|------|
| T14 | qa-engineer | T9-T13 | 前端功能测试 |
| T15 | backend-engineer | T8 | Docker Compose + 部署文档 |
| T16 | default | T15 | 推送代码到 GitHub |

---

## 微信读书同步方案

经调研，微信读书没有官方 API。采用**浏览器模拟登录 + Cookie**方案：

1. 用户在设置页填入微信读书 Cookie（有效期约 30 天）
2. 后端定期抓取书架数据（`https://weread.qq.com/web/shelf`）
3. 解析书籍列表、阅读进度、状态
4. 存入本地数据库

**备选方案：** 如果模拟登录不稳定，提供手动导入功能（CSV/JSON）。

---

## 数据库表设计概要

```sql
-- 用户表
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 任务表（支持每日任务、工作规划、目标管理）
CREATE TABLE tasks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type ENUM('daily', 'plan', 'goal') NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') DEFAULT 'pending',
    priority INT DEFAULT 0,
    due_date DATE,
    parent_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES tasks(id)
);

-- 定时任务执行记录
CREATE TABLE cron_executions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    cron_job_id VARCHAR(100) NOT NULL,
    status ENUM('success', 'failed', 'running') NOT NULL,
    result TEXT,
    executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 书籍表
CREATE TABLE books (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    weread_id VARCHAR(100),
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100),
    cover_url VARCHAR(500),
    status ENUM('want_to_read', 'reading', 'finished') DEFAULT 'want_to_read',
    progress INT DEFAULT 0,
    total_chapters INT,
    current_chapter INT,
    last_read_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 可配置化设计

所有配置通过环境变量 + `.env` 文件管理：

```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=orbit

# JWT 配置
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Hermes Cron 配置
HERMES_API_URL=http://localhost:8080
HERMES_API_KEY=your-api-key

# 微信读书配置
WEREAD_COOKIE=your-cookie

# 应用配置
APP_PORT=8000
APP_DEBUG=false
CORS_ORIGINS=http://localhost:3000
```

---

## 验收标准

每个任务完成后需满足：
1. 代码可运行，无语法错误
2. API 接口有对应的测试用例
3. 前端页面可正常展示和交互
4. 配置项通过环境变量可修改
5. README 中有清晰的使用说明
