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

## 📝 更新日志

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

---

## 📄 许可证

MIT License

---

## 👨‍💻 作者

**Moon**
- 公众号：Moon杂选
- GitHub：[@yixiqiannian](https://github.com/yixiqiannian)
