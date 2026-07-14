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
    api.get<any, TaskLog[]>('/api/task-logs', { params }),
  get: (id: number) => api.get<any, TaskLog>(`/api/task-logs/${id}`),
  create: (data: Partial<TaskLog>) => api.post('/api/task-logs', data),
  update: (id: number, data: Partial<TaskLog>) => api.put(`/api/task-logs/${id}`, data),
  delete: (id: number) => api.delete(`/api/task-logs/${id}`),
  recent: (limit?: number) => api.get<any, TaskLog[]>('/api/task-logs/recent', { params: { limit } }),
}
