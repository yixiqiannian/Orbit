import api from './index'

export interface HotlistItem {
  id: number
  source: string
  rank: number
  title: string
  url: string
  description?: string
  language?: string
  stars_today?: number
  stars_total?: number
  forks?: number
  hot_date: string
  created_at: string
}

export interface HotlistResponse {
  date: string
  source: string
  items: HotlistItem[]
}

export const hotlistApi = {
  list(params: { source?: string; hot_date?: string }) {
    return api.get<any, HotlistResponse>('/api/hotlist/', { params })
  },
  fetch(source: string = 'github') {
    return api.post<any, { message: string; count: number; date: string }>(`/api/hotlist/fetch/`, null, { params: { source } })
  },
  sources() {
    return api.get<any, { sources: { key: string; name: string; url: string }[] }>('/api/hotlist/sources/')
  }
}
