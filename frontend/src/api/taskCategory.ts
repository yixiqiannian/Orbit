import api from './index'

export interface TaskCategory {
  id: number
  name: string
  icon: string
  color: string
}

export const taskCategoryApi = {
  list() {
    return api.get<any, TaskCategory[]>('/api/task-categories')
  },
  create(data: { name: string; icon?: string; color?: string }) {
    return api.post<any, TaskCategory>('/api/task-categories', data)
  },
  delete(id: number) {
    return api.delete(`/api/task-categories/${id}`)
  }
}
