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
    api.get<any, DailyLog[]>('/api/daily-logs', { params }),
  get: (id: number) => api.get<any, DailyLog>(`/api/daily-logs/${id}`),
  create: (data: Partial<DailyLog>) => api.post('/api/daily-logs', data),
  update: (id: number, data: Partial<DailyLog>) => api.put(`/api/daily-logs/${id}`, data),
  delete: (id: number) => api.delete(`/api/daily-logs/${id}`),
  recent: (limit?: number) => api.get<any, DailyLog[]>('/api/daily-logs/recent', { params: { limit } }),
}
