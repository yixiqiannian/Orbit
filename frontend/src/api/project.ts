import api from './index'

export interface Project {
  id: number
  name: string
  description: string
  status: string
  start_date?: string
  end_date?: string
  task_count: number
  completed_count: number
  created_at: string
  updated_at?: string
}

export interface ProjectListResponse {
  items: Project[]
  total: number
}

export const projectApi = {
  list(params?: { status?: string; page?: number; size?: number }) {
    return api.get<any, ProjectListResponse>('/api/projects', { params })
  },
  getAll() {
    return api.get<any, Project[]>('/api/projects', { params: { size: 999 } })
  },
  get(id: number) {
    return api.get<any, Project>(`/api/projects/${id}`)
  },
  create(data: { name: string; description?: string; status?: string; start_date?: string; end_date?: string }) {
    return api.post<any, Project>('/api/projects', data)
  },
  update(id: number, data: Partial<Project>) {
    return api.put<any, Project>(`/api/projects/${id}`, data)
  },
  delete(id: number) {
    return api.delete(`/api/projects/${id}`)
  }
}
