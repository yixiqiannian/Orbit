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
  listCategories: () => api.get<any, KnowledgeCategory[]>('/api/knowledge/categories'),
  createCategory: (data: Partial<KnowledgeCategory>) => api.post('/api/knowledge/categories', data),
  deleteCategory: (id: number) => api.delete(`/api/knowledge/categories/${id}`),

  // 卡片
  listCards: (params?: { category_id?: number; keyword?: string }) =>
    api.get<any, KnowledgeCard[]>('/api/knowledge/cards', { params }),
  getCard: (id: number) => api.get<any, KnowledgeCard>(`/api/knowledge/cards/${id}`),
  createCard: (data: Partial<KnowledgeCard>) => api.post('/api/knowledge/cards', data),
  updateCard: (id: number, data: Partial<KnowledgeCard>) => api.put(`/api/knowledge/cards/${id}`, data),
  deleteCard: (id: number) => api.delete(`/api/knowledge/cards/${id}`),

  // 随机推送
  randomCard: () => api.get<any, KnowledgeCard>('/api/knowledge/random'),

  // 统计
  getStats: () => api.get<any, { total_categories: number; total_cards: number }>('/api/knowledge/stats'),
}
