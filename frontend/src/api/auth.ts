import api from './index'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export const authApi = {
  login(data: LoginRequest) {
    return api.post<any, LoginResponse>('/api/auth/login', data)
  },
  logout() {
    return api.post('/api/auth/logout')
  },
  getCurrentUser() {
    return api.get('/api/auth/me')
  }
}
