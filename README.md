# 🌌 Orbit - 个人管理系统

一个模块化、可配置的个人后台管理系统，帮助你管理工作规划、每日任务、目标追踪、定时任务和阅读计划。

## ✨ 功能特性

- 📊 **仪表盘** - 汇总展示所有关键信息
- 📋 **任务管理** - 每日任务 / 工作规划 / 目标管理
- ⏰ **定时任务** - 对接 Hermes Cron，页面执行，状态反馈
- 📚 **阅读规划** - 微信读书同步，书架管理，进度追踪
- 🔐 **用户认证** - JWT 登录，安全可靠
- ⚙️ **可配置化** - 所有配置通过环境变量管理

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | MySQL 8.x |
| 认证 | JWT (JSON Web Token) |
| 部署 | Docker Compose |

## 📦 项目结构

```
Orbit/
├── frontend/          # Vue 3 前端
│   ├── Dockerfile     # 前端构建 + Nginx
│   └── nginx.conf     # Nginx 配置（SPA + API 代理）
├── backend/           # FastAPI 后端
│   ├── Dockerfile     # 后端构建
│   ├── app/           # 应用代码
│   └── scripts/       # 初始化脚本
├── docker-compose.yml # Docker 编排
├── .env.example       # 环境变量示例
└── README.md          # 本文件
```

## 🚀 快速开始

### 前置条件

- Docker & Docker Compose
- Node.js 18+（仅开发时需要）

### 1. 克隆项目

```bash
git clone git@github.com:yixiqiannian/Orbit.git
cd Orbit
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的配置
# 至少需要修改：
# - DB_PASSWORD（数据库密码）
# - JWT_SECRET（建议生成随机字符串）
```

### 3. 启动服务

```bash
# 构建并启动所有服务（前端 + 后端 + 数据库）
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

> **说明：** Docker Compose 会自动创建 MySQL 数据库（使用 `.env` 中的 `DB_NAME`）。首次启动后，等待约 30 秒让数据库完成初始化，然后执行初始化脚本：

```bash
# 进入后端容器执行数据库初始化
docker exec orbit-backend bash scripts/init.sh
```

### 4. 访问应用

- 前端：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 5. 默认账户

首次启动时，系统会自动创建默认管理员账户：
- 用户名：`admin`
- 密码：`orbit2026`

**请登录后立即修改密码！**

---

## 🔧 开发模式

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 🐳 Docker 部署详解

### 服务说明

| 服务 | 容器名 | 端口 | 说明 |
|------|--------|------|------|
| frontend | orbit-frontend | 3000 | Vue 3 + Nginx |
| backend | orbit-backend | 8000 | FastAPI + Uvicorn |
| db | orbit-db | 3306 | MySQL 8.0 |

### 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重建并启动
docker-compose up -d --build

# 查看容器状态
docker-compose ps

# 查看某个服务日志
docker-compose logs -f backend

# 进入后端容器
docker exec -it orbit-backend bash

# 备份数据库
docker exec orbit-db mysqldump -u root -p orbit > backup.sql

# 恢复数据库
docker exec -i orbit-db mysql -u root -p orbit < backup.sql
```

### 数据持久化

MySQL 数据通过 Docker Volume `mysql-data` 持久化存储。即使容器被删除，数据仍然保留。

如需完全重置：
```bash
docker-compose down -v  # 删除容器和数据卷
docker-compose up -d --build
```

---

## ⚙️ 配置说明

### 数据库配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DB_HOST` | 数据库地址 | `localhost` |
| `DB_PORT` | 数据库端口 | `3306` |
| `DB_USER` | 数据库用户名 | `root` |
| `DB_PASSWORD` | 数据库密码 | - |
| `DB_NAME` | 数据库名 | `orbit` |

> **Docker Compose 模式下：** `DB_HOST` 应设为 `db`（容器名），`DB_PASSWORD` 和 `DB_NAME` 会自动传递给 MySQL 容器。

### JWT 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `JWT_SECRET` | JWT 密钥 | - |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token 过期时间（分钟） | `1440` (24小时) |

### Hermes Cron 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `HERMES_API_URL` | Hermes API 地址 | `http://localhost:8080` |
| `HERMES_API_KEY` | Hermes API 密钥 | - |

### 微信读书配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WEREAD_COOKIE` | 微信读书 Cookie | - |

**获取微信读书 Cookie：**
1. 浏览器登录 [微信读书网页版](https://weread.qq.com)
2. 打开开发者工具 (F12) → Network
3. 刷新页面，找到任意请求
4. 复制请求头中的 `Cookie` 值

---

## 📖 API 文档

启动后端后访问：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 主要 API 端点

| 模块 | 端点 | 说明 |
|------|------|------|
| 认证 | `POST /api/auth/login` | 用户登录 |
| 任务 | `GET /api/tasks` | 获取任务列表 |
| 任务 | `POST /api/tasks` | 创建任务 |
| 定时任务 | `GET /api/cron/jobs` | 获取定时任务列表 |
| 定时任务 | `POST /api/cron/jobs/{id}/run` | 执行定时任务 |
| 阅读 | `GET /api/reading/books` | 获取书架 |
| 仪表盘 | `GET /api/dashboard/stats` | 获取统计数据 |

---

## 🐛 常见问题

### 数据库连接失败

检查：
1. MySQL 服务是否启动
2. `.env` 中的数据库配置是否正确
3. 用户是否有权限访问数据库
4. Docker 模式下 `DB_HOST` 是否设为 `db`

### 前端无法访问后端

检查：
1. 后端服务是否正常运行
2. `CORS_ORIGINS` 配置是否包含前端地址
3. 网络是否通畅
4. Nginx 代理配置是否正确（`frontend/nginx.conf`）

### 微信读书同步失败

检查：
1. Cookie 是否过期（约 30 天有效期）
2. 网络是否能访问 weread.qq.com
3. 查看后端日志获取详细错误信息

### Docker 容器启动失败

```bash
# 查看所有容器状态
docker-compose ps

# 查看具体服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# 重建镜像
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 更新日志

### v1.0.0 (2026-07-13)
- 🎉 初始版本
- ✅ 用户认证系统
- ✅ 任务管理模块
- ✅ 定时任务模块
- ✅ 阅读规划模块
- ✅ 仪表盘首页
- ✅ Docker Compose 一键部署

---

## 📄 License

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 💬 联系方式

- GitHub：[@yixiqiannian](https://github.com/yixiqiannian)
- 公众号：Moon杂选
