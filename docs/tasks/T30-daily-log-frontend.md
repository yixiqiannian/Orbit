## 目标
实现每日日志的前端页面，包括日志列表、编辑和仪表盘显示。

## 前置任务
依赖 T29 完成

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 创建 API (api/dailyLog.ts)
```typescript
import api from './index'

export interface DailyLog {
  id: number
  date: string
  title: string
  content: string
  mood: string
  tags: string
  created_at: string
  updated_at: string
}

export const dailyLogApi = {
  list: (params?: { start_date?: string; end_date?: string; limit?: number }) => 
    api.get<DailyLog[]>('/api/daily-logs', { params }),
  get: (id: number) => api.get<DailyLog>(`/api/daily-logs/${id}`),
  create: (data: Partial<DailyLog>) => api.post('/api/daily-logs', data),
  update: (id: number, data: Partial<DailyLog>) => api.put(`/api/daily-logs/${id}`, data),
  delete: (id: number) => api.delete(`/api/daily-logs/${id}`),
  recent: (limit?: number) => api.get<DailyLog[]>('/api/daily-logs/recent', { params: { limit } }),
}
```

### 2. 创建日志页面 (views/DailyLogs.vue)
功能要求：
- 日志列表（按日期倒序）
- 每条日志显示：日期、标题、心情、标签
- 支持新增日志（弹窗，内容用 textarea，支持 Markdown）
- 支持编辑/删除日志
- 支持按日期范围筛选
- 心情选择：😊 好 / 😐 一般 / 😢 差
- Markdown 渲染内容

### 3. 更新仪表盘 (views/Dashboard.vue)
添加「最近日志」卡片：
- 显示最近5条日志
- 每条显示：日期、标题、心情
- 点击跳转到日志页面

### 4. 更新侧边栏 (components/Sidebar.vue)
添加菜单项：每日日志

### 5. 更新路由 (router/index.ts)
添加路由：
```typescript
{
  path: '/daily-logs',
  name: 'DailyLogs',
  component: () => import('../views/DailyLogs.vue'),
  meta: { requiresAuth: true }
}
```

### 6. 验收标准
- [ ] 日志列表显示正常
- [ ] 新增/编辑/删除日志正常
- [ ] Markdown 渲染正常
- [ ] 日期筛选正常
- [ ] 仪表盘显示最近日志
- [ ] 侧边栏菜单正常
