# 🌌 Orbit - 个人管理系统

一个模块化、可配置的个人后台管理系统，帮助你管理工作规划、每日任务、目标追踪、定时任务和阅读计划。

## ✨ 功能特性

### 📊 仪表盘
- 统计卡片（任务、定时任务、阅读、导航、邮箱）
- 任务完成热力图（GitHub 风格）
- 即将过期任务提醒
- 项目进度展示
- 每日一记（随机知识卡片）
- 最近日志

### 📋 任务管理
- 每日任务 / 工作规划 / 目标管理（卡片布局）
- 任务分类（自定义：学习、工作、生活等）
- 项目管理（长期规划 + 周任务）
- 任务日志（笔记、问题、知识点、进度）
- 过期提示（已过期红色、即将过期橙色）
- 任务归档（按月归档，文件夹形式查看）

### ⏰ 定时任务
- 对接 Hermes Cron
- 页面执行，状态反馈
- 执行历史记录

### 📚 阅读规划
- 微信读书同步
- 书架管理，进度追踪
- 阅读统计

### 📝 每日日志
- 工作总结、学习笔记
- 心情记录（😊好/😐一般/😢差）
- Markdown 支持
- 按日期筛选

### 🧠 知识卡片
- 分类管理（Linux、Docker、K8s等）
- Markdown 内容
- 仪表盘随机推送

### 📧 邮箱管理
- 多邮箱配置（163、QQ、Gmail）
- 收件箱、未读统计
- 发送邮件

### 🧭 导航管理
- 自定义导航分类
- 前台独立展示页（/portal）
- 自动识别网站信息

### 🔥 热榜
- GitHub Trending 每日热榜抓取（数据源可扩展）
- 日期选择，查看历史热榜
- 排名徽章（金银铜）、Star/Fork 统计、语言标签
- 手动抓取，幂等去重入库

### 📖 每日一言
- Header 居中展示每日一言（内置名言库，按日期固定一条）
- 支持浅色/深色模式

### 🔐 用户认证
- JWT 登录
- 安全可靠

---

## 🛠️ 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 后端 | Python FastAPI + SQLAlchemy |
| 数据库 | MySQL 8.x |
| 认证 | JWT (JSON Web Token) |
| 定时任务 | Hermes Cron |

---

## 📦 项目结构

```
Orbit/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/          # API 接口（含 hotlist.py 热榜）
│   │   ├── core/         # 配置、认证、数据库
│   │   ├── models/       # 数据模型（含 hotlist_item.py）
│   │   ├── schemas/      # 数据验证
│   │   └── services/     # 业务逻辑（含 github_trending.py 抓取）
│   ├── scripts/          # 初始化脚本
│   └── requirements.txt
├── frontend/             # Vue 3 前端
│   └── src/
│       ├── api/          # API 封装
│       ├── views/        # 页面组件
│       ├── components/   # 公共组件
│       ├── stores/       # 状态管理
│       └── router/       # 路由配置
├── .env.example          # 环境变量示例
├── .gitignore
├── start.bat             # Windows 一键启动脚本
└── README.md
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.x

### 1. 克隆项目

```bash
git clone https://github.com/yixiqiannian/Orbit.git
cd Orbit
```

### 2. 配置环境变量

```bash
# 复制示例文件
cp .env.example backend/.env

# 编辑配置
# 修改数据库连接、JWT密钥等
```

### 3. 初始化数据库

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 创建数据库
mysql -u root -p -e "CREATE DATABASE orbit CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 初始化表
python scripts/init_db.py

# 创建管理员
python scripts/init_admin.py
```

### 4. 启动后端

```bash
cd backend
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 6. 访问系统

- 前端：http://localhost:5173
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

**默认登录：**
- 用户名：`admin`
- 密码：`orbit2026`

---

## ⚙️ 配置说明

### 后端配置（backend/.env）

```bash
# 数据库
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=orbit

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# 应用
APP_PORT=8000
APP_DEBUG=true

# CORS（前端地址）
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# 微信读书（可选）
WEREAD_API_KEY=your_api_key
```

### 前端配置（frontend/.env）

```bash
# 后端 API 地址
VITE_API_BASE_URL=http://localhost:8000
```

---

## 🐳 Docker 部署

### 构建镜像

```bash
# 后端
cd backend
docker build -t orbit-backend .

# 前端
cd frontend
docker build -t orbit-frontend .
```

### 启动容器

```bash
# 创建网络
docker network create orbit-net

# 启动 MySQL
docker run -d \
  --name orbit-mysql \
  --network orbit-net \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=orbit \
  -p 3306:3306 \
  mysql:8.0

# 启动后端
docker run -d \
  --name orbit-backend \
  --network orbit-net \
  -e DB_HOST=orbit-mysql \
  -e DB_PASSWORD=your_password \
  -e JWT_SECRET=your_secret \
  -p 8000:8000 \
  orbit-backend

# 启动前端
docker run -d \
  --name orbit-frontend \
  --network orbit-net \
  -p 5173:80 \
  orbit-frontend
```

### Nginx 配置（前端容器内）

```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://orbit-backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🔥 热榜模块说明

### 数据源

当前内置 **GitHub Trending**（每日），数据源注册表位于 `backend/app/api/hotlist.py` 的 `SOURCES` 常量。新增数据源只需：写一个抓取函数 + 在 `SOURCES` 注册，前端自动出现对应 tab。

### 抓取方式

两种方式：
1. **页面手动抓取**：进入「热榜」页点击「立即抓取」（需登录）
2. **API 定时抓取**（推荐，配合 Hermes Cron 每日自动执行）：
   ```bash
   curl -X POST "http://localhost:8000/api/hotlist/fetch/?source=github" \
     -H "Authorization: Bearer <你的JWT>"
   ```
   抓取按 `source + hot_date + rank` 幂等去重，同一天重复抓取不会产生重复数据。

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/hotlist/?source=github&hot_date=2026-08-13` | GET | 查询某日热榜（默认今天） |
| `/api/hotlist/fetch/?source=github` | POST | 抓取最新热榜入库 |
| `/api/hotlist/sources/` | GET | 列出可用数据源 |

### Docker 部署注意（新表迁移）

**FastAPI/SQLAlchemy 不会自动建表！** 热榜功能需要手动在 MySQL 创建 `hotlist_items` 表：

```sql
CREATE TABLE IF NOT EXISTS hotlist_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(50) NOT NULL DEFAULT 'github',
  rank INT NOT NULL,
  title VARCHAR(300) NOT NULL,
  url VARCHAR(500) NOT NULL,
  description TEXT NULL,
  language VARCHAR(50) NULL,
  stars_today INT NULL,
  stars_total INT NULL,
  forks INT NULL,
  hot_date DATE NOT NULL,
  created_at DATETIME,
  UNIQUE KEY uq_hotlist_source_date_rank (source, hot_date, rank)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```bash
# 进入 MySQL 容器执行
docker exec -it orbit-mysql mysql -u root -p orbit -e "CREATE TABLE IF NOT EXISTS hotlist_items (...);"
# 然后重启后端使模型生效
docker restart orbit-backend
```

本地开发环境直接运行 `python scripts/init_db.py` 即可自动建表。

---

## 📝 更新日志

### v1.1.1 (2026-08-13)
- 新增「每日一言」：Header 居中展示，内置 70 条中英名言库，按日期固定一条，离线可用

### v1.1.0 (2026-08-13)
- 新增「热榜」模块：GitHub Trending 每日热榜
- 后端：`hotlist_items` 表、抓取服务（httpx + BeautifulSoup）、`/api/hotlist/` API（查询/抓取/数据源）
- 前端：`/hotlist` 页面（日期选择、手动抓取、排名徽章、深/浅色模式）
- 数据源架构可扩展，后续可接入知乎/微博/V2EX 等

### v1.0.0 (2026-07-29)
- 初始版本发布
- 任务管理（每日任务/工作规划/目标管理）
- 定时任务（对接 Hermes Cron）
- 阅读规划（微信读书同步）
- 邮箱管理（163/QQ/Gmail）
- 导航管理
- 知识卡片
- 每日日志
- 仪表盘（热力图、统计、图表）
- 任务归档（按月归档，文件夹形式查看）
- 任务分类和项目管理

---

## 📄 许可证

MIT License

---

## 👨‍💻 作者

**Moon**
- 公众号：Moon杂选
- GitHub：[@yixiqiannian](https://github.com/yixiqiannian)
