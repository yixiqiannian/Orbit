# 🌌 Orbit - 个人管理系统

一个模块化、可配置的个人后台管理系统，帮助你管理工作规划、每日任务、目标追踪、定时任务和阅读计划。

## ✨ 功能特性

- 📊 **仪表盘** - 汇总展示所有关键信息
- 📋 **任务管理** - 每日任务 / 工作规划 / 目标管理（卡片布局）
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

## 📦 项目结构

```
Orbit/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 接口
│   │   ├── core/         # 配置、认证、数据库
│   │   ├── models/       # 数据模型
│   │   ├── schemas/      # 数据验证
│   │   └── services/     # 业务逻辑
│   ├── scripts/          # 初始化脚本
│   └── requirements.txt
├── frontend/             # Vue 3 前端
│   └── src/
│       ├── api/          # API 封装
│       ├── views/        # 页面组件
│       ├── stores/       # 状态管理
│       └── router/       # 路由配置
├── .env.example          # 环境变量示例
├── .gitignore
├── start.bat             # Windows 一键启动脚本
└── README.md
```

---

## 🚀 快速开始

### 前置条件

- **Python 3.11+**（推荐 3.11，3.14 可能有兼容问题）
- **Node.js 18+**
- **MySQL 8.x**（本地或远程）

### 1. 克隆项目

```bash
git clone git@github.com:yixiqiannian/Orbit.git
cd Orbit
```

### 2. 创建数据库

打开 MySQL 命令行或 Navicat，执行：

```sql
CREATE DATABASE orbit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 配置后端

```bash
cd backend

# 复制环境变量示例
cp ../.env.example .env

# 编辑 .env 文件，填入你的配置
```

**.env 配置说明：**

```env
# 数据库配置（必填）
DB_HOST=localhost          # 数据库地址
DB_PORT=3306               # 数据库端口
DB_USER=root               # 数据库用户名
DB_PASSWORD=your_password  # 数据库密码
DB_NAME=orbit              # 数据库名

# JWT 配置（建议修改）
JWT_SECRET=your-secret-key-here  # JWT 密钥，建议随机生成
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440          # Token 有效期（分钟）

# 微信读书配置（可选）
WEREAD_API_KEY=wrk-xxxxxx  # 微信读书 API Key

# 应用配置
APP_DEBUG=false
CORS_ORIGINS=http://localhost:5173  # 前端地址
```

### 4. 初始化后端

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库表
python scripts/init_db.py

# 创建默认管理员账户
python scripts/init_admin.py
```

**预期输出：**
```
Database tables created successfully!
Admin user created: admin / orbit2026
```

### 5. 启动后端

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**预期输出：**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 6. 配置并启动前端

打开新的终端窗口：

```bash
cd frontend

# 创建环境变量文件
echo VITE_API_BASE_URL=http://localhost:8000 > .env

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

**预期输出：**
```
VITE v8.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### 7. 访问系统

打开浏览器访问 **http://localhost:5173**

**默认登录账户：**
- 用户名：`admin`
- 密码：`orbit2026`

⚠️ **请登录后立即修改密码！**

---

## 🪟 Windows 一键启动

双击 `start.bat` 文件即可同时启动前后端。

---

## 📖 功能说明

### 仪表盘

首页汇总展示：
- 任务统计（待办、进行中、今日完成、逾期）
- 定时任务状态
- 阅读统计（总书籍、在读、已读、平均进度）
- 最近任务和执行记录

### 任务管理

支持三种任务类型：
- **每日任务** - 每天需要完成的任务
- **工作规划** - 阶段性工作计划
- **目标管理** - 长期目标追踪

功能：
- 卡片布局，直观展示
- 优先级标记（普通/重要/紧急）
- 状态切换（待办/进行中/已完成/已取消）
- 截止日期设置

### 定时任务

对接 Hermes Cron，展示所有定时任务：
- 调度规则（cron 表达式）
- 上次执行时间
- 执行状态（成功/失败）
- 立即执行功能

### 阅读规划

集成微信读书 API：
- 书架同步（自动导入微信读书书籍）
- 阅读进度追踪
- 状态管理（想读/在读/已读）
- 单本书进度同步
- 阅读统计

---

## 🔧 配置详解

### 数据库配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DB_HOST` | 数据库地址 | `localhost` |
| `DB_PORT` | 数据库端口 | `3306` |
| `DB_USER` | 数据库用户名 | `root` |
| `DB_PASSWORD` | 数据库密码 | - |
| `DB_NAME` | 数据库名 | `orbit` |

支持远程 MySQL，只需修改 `DB_HOST` 为远程地址。

### JWT 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `JWT_SECRET` | JWT 密钥 | `change-this` |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token 过期时间 | `1440` |

生成随机密钥：
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 微信读书配置

| 变量 | 说明 |
|------|------|
| `WEREAD_API_KEY` | 微信读书 API Key（格式：`wrk-xxxxxx`） |

获取方式：联系微信读书官方申请 API Key。

---

## 🐛 常见问题

### 1. 数据库连接失败

```
pymysql.err.OperationalError: (1045, "Access denied")
```

**解决方案：**
- 检查 `.env` 中的数据库密码是否正确
- 确认 MySQL 服务已启动
- 确认用户有权限访问数据库

### 2. Python 版本不兼容

```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument
```

**解决方案：**
使用 Python 3.11 或 3.12，不要使用 3.14。

```bash
# 删除旧的虚拟环境
rmdir /s /q venv

# 使用 Python 3.11 创建
C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
```

### 3. 前端无法访问

```
ERR_CONNECTION_REFUSED
```

**解决方案：**
- 确认前端已启动（端口 5173）
- 尝试访问 http://127.0.0.1:5173
- 检查防火墙设置

### 4. CORS 错误

```
Access to XMLHttpRequest has been blocked by CORS
```

**解决方案：**
确认 `.env` 中 `CORS_ORIGINS` 包含前端地址。

### 5. 微信读书同步失败

**解决方案：**
- 检查 `WEREAD_API_KEY` 是否正确
- 确认 API Key 未过期
- 检查网络连接

---

## 📝 API 文档

启动后端后访问：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 主要 API 端点

| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 认证 | `/api/auth/login` | POST | 用户登录 |
| 认证 | `/api/auth/me` | GET | 获取当前用户 |
| 任务 | `/api/tasks` | GET | 获取任务列表 |
| 任务 | `/api/tasks` | POST | 创建任务 |
| 任务 | `/api/tasks/{id}` | PUT | 更新任务 |
| 任务 | `/api/tasks/{id}` | DELETE | 删除任务 |
| 定时任务 | `/api/cron/jobs/list` | GET | 获取定时任务列表 |
| 定时任务 | `/api/cron/jobs/{id}/run` | POST | 执行定时任务 |
| 阅读 | `/api/reading/books` | GET | 获取书架 |
| 阅读 | `/api/reading/sync` | POST | 同步微信读书 |
| 阅读 | `/api/reading/sync/{id}` | GET | 同步单本书进度 |
| 仪表盘 | `/api/dashboard` | GET | 获取统计数据 |

---

## 🔄 更新日志

### v1.1.0 (2026-07-13)
- ✅ 定时任务页面显示 Hermes 定时任务
- ✅ 微信读书同步获取阅读进度
- ✅ 任务和阅读页面改为卡片布局
- ✅ 修复 CORS 配置问题
- ✅ 修复 Python 3.14 兼容问题

### v1.0.0 (2026-07-13)
- 🎉 初始版本
- ✅ 用户认证系统
- ✅ 任务管理模块
- ✅ 定时任务模块
- ✅ 阅读规划模块
- ✅ 仪表盘首页

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
