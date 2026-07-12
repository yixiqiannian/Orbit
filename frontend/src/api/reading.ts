import api from './index'

export interface Book {
  id: number
  title: string
  author?: string
  status: 'want_to_read' | 'reading' | 'finished'
  progress: number
  current_chapter: number
  total_chapters: number
  created_at: string
  updated_at: string
}

export interface ReadingStats {
  total_books: number
  reading: number
  finished: number
  avg_progress: number
}

export interface BookListResponse {
  items: Book[]
  total: number
  page: number
  size: number
}

export const readingApi = {
  listBooks(params: { status?: string; page?: number; size?: number }) {
    return api.get<any, BookListResponse>('/api/reading/books', { params })
  },
  createBook(data: { title: string; author?: string; status?: string }) {
    return api.post<any, Book>('/api/reading/books', data)
  },
  updateBook(id: number, data: { status?: string; progress?: number; current_chapter?: number; total_chapters?: number }) {
    return api.put<any, Book>(`/api/reading/books/${id}`, data)
  },
  deleteBook(id: number) {
    return api.delete(`/api/reading/books/${id}`)
  },
  getStats() {
    return api.get<any, ReadingStats>('/api/reading/stats')
  },
  syncWeread() {
    return api.post('/api/reading/sync')
  }
}
