# Orbit 前端 UI 改造计划（UI/UX Pro Max 设计系统落地）

> **For Hermes:** 用 kanban 分配任务给 frontend-engineer / qa-engineer，逐个验收。

**Goal:** 将 Orbit 前端从 Element Plus 默认主题升级为 ui-ux-pro-max 生成的设计系统（深蓝 #1E40AF + 琥珀 #D97706、Fira 字体、高密度仪表盘风格、去除 emoji 图标）。

**设计系统来源:** `G:\Orbit\design-system\orbit\MASTER.md`（已用 ui-ux-pro-max 生成并持久化）

**Tech Stack:** Vue3 + Element Plus 2.14 + Vite 8 + TypeScript

---

## 设计 Token（来自 MASTER.md）

| Role | Hex | CSS Variable |
|------|-----|--------------|
| Primary | `#1E40AF` | `--color-primary` |
| On Primary | `#FFFFFF` | `--color-on-primary` |
| Secondary | `#3B82F6` | `--color-secondary` |
| Accent/CTA | `#D97706` | `--color-accent` |
| Background | `#F8FAFC` | `--color-background` |
| Foreground | `#1E3A8A` | `--color-foreground` |
| Muted | `#E9EEF6` | `--color-muted` |
| Border | `#DBEAFE` | `--color-border` |
| Destructive | `#DC2626` | `--color-destructive` |
| Ring | `#1E40AF` | `--color-ring` |

**字体:** Fira Sans（正文）+ Fira Code（标题/数据），Google Fonts import
**密度:** 8/10（密集仪表盘：卡片 padding 16px、间距 16px）
**风格:** Data-Dense Dashboard，Light/Dark 双模式支持，WCAG AA

---

## 任务列表

### Task 1: 全局设计 token + Element Plus 主题覆盖

**Objective:** 创建 CSS 变量文件并覆盖 Element Plus 主题色，全局生效。

**Files:**
- Create: `frontend/src/assets/design-tokens.css`
- Modify: `frontend/src/main.ts`（import token 文件 + 字体）
- Modify: `frontend/src/App.vue`（全局样式：字体、背景色）

**要点:**
1. `design-tokens.css` 定义上述 CSS 变量（含 light/dark 模式变量）
2. 覆盖 Element Plus 主题：`--el-color-primary: #1E40AF` 及 light-3/5/7/8/9、dark-2 变体（用 color-mix 或手写）
3. main.ts 引入 `@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Fira+Sans:wght@300;400;500;600;700&display=swap')` + `import './assets/design-tokens.css'`
4. body 字体设为 Fira Sans，页面背景 #F8FAFC

**验证:** `npx vite build` 通过；浏览器打开页面背景/主色生效

---

### Task 2: 布局与侧边栏改造

**Objective:** Sidebar/Layout/Header 应用新配色，侧边栏从 #304156 改为深蓝系。

**Files:**
- Modify: `frontend/src/components/Layout.vue`
- Modify: `frontend/src/components/Sidebar.vue`
- Modify: `frontend/src/components/Header.vue`

**要点:**
1. 侧边栏背景 `#1E3A8A`（foreground 深蓝）或 `#111827` 深色，文字 #E9EEF6
2. el-menu 背景色与侧边栏一致，active 项高亮 `#3B82F6`/白底渐变
3. Header 白色背景 + 底部 border #DBEAFE
4. Logo "Orbit" 用 Fira Code 加粗
5. 保持 collapse 折叠功能不变

**验证:** 侧边栏/顶栏配色生效，菜单高亮正确

---

### Task 3: 登录页改造

**Objective:** 登录页从紫色渐变改为新设计系统风格。

**Files:**
- Modify: `frontend/src/views/Login.vue`

**要点:**
1. 背景改为深蓝渐变（#1E40AF → #1E3A8A）或极简 #F8FAFC + 居中卡片
2. 标题去掉 emoji `🌌`，改为 "Orbit" 文字 logo（Fira Code）
3. 登录按钮用 --el-color-primary
4. 卡片阴影、圆角 12px，符合现代风格

**验证:** 登录页渲染正常，配色符合设计 token

---

### Task 4: Dashboard 仪表盘改造

**Objective:** 统计卡片去 emoji、用 Element Plus 图标，卡片样式统一。

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`
- Modify: `frontend/src/components/TaskHeatmap.vue`

**要点:**
1. 所有卡片 header 的 emoji（📊📋⏰📚🧭📦✅🧠📁）替换为 Element Plus 图标组件
2. 统计卡片：数值用 Fira Code 大号数字，hover 阴影过渡 150-300ms
3. 热力图颜色保持 GitHub 绿（#ebedf0 → #216e39）或对齐 primary 蓝
4. 卡片间距统一 16-20px，border 用 #DBEAFE

**验证:** 页面无 emoji 图标残留（grep emoji 检查），卡片样式统一

---

### Task 5: 其余页面统一清理

**Objective:** 所有页面标题 emoji 清理 + 卡片/表格样式统一。

**Files:**
- Modify: `frontend/src/views/Tasks.vue`、`CronJobs.vue`、`Reading.vue`、`Email.vue`、`NavManage.vue`、`NavPortal.vue`、`Knowledge.vue`、`DailyLogs.vue`、`Archives.vue`、`Projects.vue`

**要点:**
1. 页面标题 `<h2>📊 xxx</h2>` 去掉 emoji，保留文字
2. 按钮/标签/卡片视觉统一（由全局 token 自动生效，尽量少改业务逻辑）
3. NavPortal 是独立暗色页，保持暗色但色值对齐新 token

**验证:** `grep -P '[\x{1F300}-\x{1FAFF}]' views/*.vue` 无 emoji 命中（除日期/内容数据）

---

### Task 6: QA 验收

**Objective:** 本地启动前后端，浏览器实测所有页面渲染与交互。

**Files:** 无代码改动，仅测试

**要点:**
1. 启动后端（venv uvicorn :8000）+ 前端（vite :5173）
2. 用 browser-harness 连接本地 Chrome，登录 admin/orbit2026
3. 逐页截图：Dashboard/Tasks/Cron/Reading/Email/Nav/Knowledge/DailyLogs/Archives/Login
4. 检查：配色、emoji 残留、控制台报错、布局错乱

**验证:** 各页截图无异常，控制台无报错，用户可看到截图确认

---

## 执行顺序

Task 1 → 2 → 3 → 4 → 5 由 frontend-engineer 顺序执行（依赖全局 token），Task 6 由 qa-engineer 最后验收。

## 部署说明（用户自己执行）

```bash
cd /g/Orbit/frontend && npx vite build
# 本地测试后，再按 orbit-fullstack skill 的 Docker 流程部署到 47.110.74.114
```
