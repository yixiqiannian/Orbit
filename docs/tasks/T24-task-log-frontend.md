## 目标
实现任务日志的前端功能，包括任务详情页的日志时间线和仪表盘的最近日志。

## 前置任务
依赖 T23 完成

## 工作目录
G:\Orbit\frontend

## 任务要求

### 1. 创建 API (api/taskLog.ts)
```typescript
import api from './index'

export interface TaskLog {
  id: number
  task_id: number
  content: string
  log_type: string
  created_at: string
  updated_at: string
}

export const taskLogApi = {
  list: (params?: { task_id?: number; log_type?: string; limit?: number }) => 
    api.get<TaskLog[]>('/api/task-logs', { params }),
  get: (id: number) => api.get<TaskLog>(`/api/task-logs/${id}`),
  create: (data: Partial<TaskLog>) => api.post('/api/task-logs', data),
  update: (id: number, data: Partial<TaskLog>) => api.put(`/api/task-logs/${id}`, data),
  delete: (id: number) => api.delete(`/api/task-logs/${id}`),
  recent: (limit?: number) => api.get<TaskLog[]>('/api/task-logs/recent', { params: { limit } }),
}
```

### 2. 创建日志组件 (components/TaskLogTimeline.vue)
功能要求：
- 显示某个任务的日志时间线
- 每条日志显示：时间、类型标签、内容（Markdown渲染）
- 支持新增日志（弹窗，内容用textarea，支持Markdown）
- 支持编辑/删除日志
- 类型选择：笔记(note)、问题(problem)、知识点(knowledge)、进度(progress)

类型标签颜色：
- note: 蓝色（笔记）
- problem: 红色（问题）
- knowledge: 绿色（知识点）
- progress: 橙色（进度）

### 3. 更新任务管理页面 (views/Tasks.vue)
功能要求：
- 任务卡片添加「日志」按钮
- 点击「日志」打开详情弹窗
- 弹窗左侧显示任务信息，右侧显示日志时间线

### 4. 更新仪表盘 (views/Dashboard.vue)
功能要求：
- 添加「最近学习日志」卡片
- 显示最近5条日志
- 每条显示：任务标题、日志类型、内容预览、时间
- 点击跳转到任务管理页面

### 5. 更新 Dashboard API (api/dashboard.ts)
添加 recent_logs 字段

### 6. 验收标准
- [ ] 日志时间线显示正常
- [ ] 新增/编辑/删除日志正常
- [ ] Markdown 渲染正常
- [ ] 类型标签颜色正确
- [ ] 仪表盘最近日志显示正常
