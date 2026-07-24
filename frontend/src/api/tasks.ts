import api from './index'

export interface Task {
  id: number
  title: string
  type: string
  description?: string
  status: string
  priority: string
  category_id?: number
  category_name?: string
  project_id?: number
  project_name?: string
  due_date?: string
  created_at: string
  updated_at?: string
}

export interface TaskListResponse {
  items: Task[]
  total: number
}

export const taskApi = {
  list(params?: { type?: string; status?: string; page?: number; size?: number }) {
    return api.get<any, TaskListResponse>('/api/tasks', { params })
  },
  create(data: {
    title: string
    type: string
    description?: string
    priority?: string
    category_id?: number
    project_id?: number
    due_date?: string
  }) {
    return api.post<any, Task>('/api/tasks', data)
  },
  update(id: number, data: { title?: string; status?: string; priority?: string; category_id?: number; project_id?: number; due_date?: string }) {
    return api.put<any, Task>(`/api/tasks/${id}`, data)
  },
  delete(id: number) {
    return api.delete(`/api/tasks/${id}`)
  },
  getToday() {
    return api.get<any, TaskListResponse>('/api/tasks/today')
  }
}
