## 目标
实现导航网站的前端页面，包括后台管理页面和单独的前台展示页。

## 前置任务
依赖 T19 完成

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 创建 API (api/nav.ts)
```typescript
export interface NavCategory {
  id: number
  name: string
  icon?: string
  sort_order: number
}

export interface NavSite {
  id: number
  category_id: number
  name: string
  url: string
  icon?: string
  description?: string
  sort_order: number
  category?: NavCategory
}

export const navApi = {
  listCategories() { ... },
  createCategory(data) { ... },
  updateCategory(id, data) { ... },
  deleteCategory(id) { ... },
  listSites(categoryId?) { ... },
  createSite(data) { ... },
  updateSite(id, data) { ... },
  deleteSite(id) { ... },
  getStats() { ... }
}
```

### 2. 创建后台管理页面 (views/NavManage.vue)
- 左侧分类列表，支持增删改
- 右侧导航列表，支持增删改
- 添加/编辑对话框

### 3. 创建前台展示页面 (views/NavPortal.vue)
- 独立页面，不使用后台 Layout
- 按分类展示导航卡片
- 卡片显示图标、名称、描述
- 点击在新窗口打开
- 搜索功能
- 美观的暗色主题设计

### 4. 更新路由 (router/index.ts)
```typescript
// 后台管理路由
{
  path: '/nav',
  name: 'NavManage',
  component: () => import('../views/NavManage.vue')
}

// 前台展示路由（独立页面）
{
  path: '/portal',
  name: 'NavPortal',
  component: () => import('../views/NavPortal.vue'),
  meta: { requiresAuth: false }
}
```

### 5. 更新侧边栏 (components/Sidebar.vue)
添加「导航管理」菜单项

### 6. 更新仪表盘 (views/Dashboard.vue)
添加导航统计卡片

## 前台展示页设计要求
- 暗色背景 (#1a1a2e)
- 分类标签横向排列
- 导航卡片网格布局
- 卡片 hover 效果
- 顶部搜索框
- 响应式设计

## 验收标准
- [ ] 后台管理页面正常工作
- [ ] 前台展示页面独立可访问
- [ ] 分类和导航 CRUD 正常
- [ ] 仪表盘显示导航统计
- [ ] /portal 页面美观可用
