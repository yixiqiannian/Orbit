## 目标
实现知识卡片（记忆卡片）的前端页面，包括后台管理页面和仪表盘随机推送。

## 前置任务
依赖 T21 完成

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 创建 API (api/knowledge.ts)
```typescript
import api from './index'

export interface KnowledgeCategory {
  id: number
  name: string
  icon: string
  color: string
  sort_order: number
  card_count: number
}

export interface KnowledgeCard {
  id: number
  category_id: number
  category_name: string
  title: string
  content: string
  tags: string
  created_at: string
  updated_at: string
}

export const knowledgeApi = {
  // 分类
  listCategories: () => api.get<KnowledgeCategory[]>('/api/knowledge/categories'),
  createCategory: (data: Partial<KnowledgeCategory>) => api.post('/api/knowledge/categories', data),
  deleteCategory: (id: number) => api.delete(`/api/knowledge/categories/${id}`),
  
  // 卡片
  listCards: (params?: { category_id?: number; keyword?: string }) => 
    api.get<KnowledgeCard[]>('/api/knowledge/cards', { params }),
  getCard: (id: number) => api.get<KnowledgeCard>(`/api/knowledge/cards/${id}`),
  createCard: (data: Partial<KnowledgeCard>) => api.post('/api/knowledge/cards', data),
  updateCard: (id: number, data: Partial<KnowledgeCard>) => api.put(`/api/knowledge/cards/${id}`, data),
  deleteCard: (id: number) => api.delete(`/api/knowledge/cards/${id}`),
  
  // 随机推送
  randomCard: () => api.get<KnowledgeCard>('/api/knowledge/random'),
  
  // 统计
  getStats: () => api.get('/api/knowledge/stats'),
}
```

### 2. 创建知识卡片管理页面 (views/Knowledge.vue)
功能要求：
- 左侧：分类列表（分栏），点击分类筛选卡片
- 右侧：卡片列表，每个卡片显示标题、标签、预览
- 支持新增分类（弹窗输入名称、图标、颜色）
- 支持新增卡片（弹窗，标题 + 内容用 textarea，支持 Markdown）
- 支持编辑卡片（弹窗）
- 支持删除卡片
- 支持搜索卡片

### 3. 创建卡片详情弹窗 (components/CardDetail.vue)
功能要求：
- 显示卡片标题、分类、标签
- 用 Markdown 渲染内容（使用 v-html 或 markdown-it）
- 支持关闭

### 4. 更新仪表盘 (views/Dashboard.vue)
功能要求：
- 添加「每日一记」卡片
- 调用 /api/knowledge/random 获取随机卡片
- 显示卡片标题、分类、内容预览
- 点击跳转到知识卡片页面

### 5. 更新路由 (router/index.ts)
添加路由：
```typescript
{
  path: '/knowledge',
  name: 'Knowledge',
  component: () => import('../views/Knowledge.vue'),
  meta: { requiresAuth: true }
}
```

### 6. 更新侧边栏 (App.vue 或 Layout)
添加菜单项：知识卡片

### 7. 验收标准
- [ ] 分类列表显示正常
- [ ] 卡片 CRUD 正常
- [ ] Markdown 渲染正常
- [ ] 随机推送显示正常
- [ ] 点击跳转正常
