import api from './index'

export interface NavCategory {
  id: number
  name: string
  icon?: string
  sort_order: number
  created_at: string
}

export interface NavSite {
  id: number
  category_id: number
  name: string
  url: string
  icon?: string
  description?: string
  sort_order: number
  created_at: string
  category?: NavCategory
}

export interface NavStats {
  total_categories: number
  total_sites: number
}

export const navApi = {
  listCategories() {
    return api.get<any, NavCategory[]>('/api/nav/categories')
  },
  createCategory(data: { name: string; icon?: string; sort_order?: number }) {
    return api.post<any, NavCategory>('/api/nav/categories', data)
  },
  updateCategory(id: number, data: { name?: string; icon?: string; sort_order?: number }) {
    return api.put<any, NavCategory>(`/api/nav/categories/${id}`, data)
  },
  deleteCategory(id: number) {
    return api.delete(`/api/nav/categories/${id}`)
  },
  listSites(categoryId?: number) {
    return api.get<any, { total: number; items: NavSite[] }>('/api/nav/sites', {
      params: categoryId ? { category_id: categoryId } : {}
    })
  },
  createSite(data: { category_id: number; name: string; url: string; icon?: string; description?: string; sort_order?: number }) {
    return api.post<any, NavSite>('/api/nav/sites', data)
  },
  updateSite(id: number, data: { category_id?: number; name?: string; url?: string; icon?: string; description?: string; sort_order?: number }) {
    return api.put<any, NavSite>(`/api/nav/sites/${id}`, data)
  },
  deleteSite(id: number) {
    return api.delete(`/api/nav/sites/${id}`)
  },
  getStats() {
    return api.get<any, NavStats>('/api/nav/stats')
  }
}
