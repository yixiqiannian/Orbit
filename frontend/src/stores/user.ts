import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '../api/auth'

export interface UserInfo {
  id: string
  username: string
  email?: string
  avatar?: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)
  const isLoggedIn = computed(() => !!token.value)

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function clearToken() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  async function login(username: string, password: string) {
    const res = await authApi.login({ username, password })
    setToken(res.access_token)
    await fetchUser()
    return res
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearToken()
    }
  }

  async function fetchUser() {
    try {
      const res = await authApi.getCurrentUser()
      userInfo.value = res as any
    } catch {
      clearToken()
    }
  }

  // Initialize user info if token exists on page load
  if (token.value) {
    fetchUser()
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    setToken,
    clearToken,
    login,
    logout,
    fetchUser
  }
})
