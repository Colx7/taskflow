import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, register as registerApi, getMe } from '@/api/auth'
import type { LoginParams, RegisterParams, TokenData } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<TokenData['user'] | null>(null)
  const token = ref<string>('')

  const isAuthenticated = computed(() => !!token.value)

  // 从 localStorage 恢复登录态
  const savedToken = localStorage.getItem('token')
  const savedUser = localStorage.getItem('user')
  if (savedToken) token.value = savedToken
  if (savedUser) user.value = JSON.parse(savedUser)

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password })
    token.value = res.token
    user.value = res.user
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user))
  }

  async function register(username: string, email: string, password: string) {
    const res = await registerApi({ username, email, password })
    token.value = res.token
    user.value = res.user
    localStorage.setItem('token', res.token)
    localStorage.setItem('user', JSON.stringify(res.user))
  }

  async function fetchUser() {
    const data = await getMe()
    user.value = {
      id: data.id,
      username: data.username,
      email: data.email,
      avatar_url: data.avatar_url,
      created_at: data.created_at,
    }
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { user, token, isAuthenticated, login, register, fetchUser, logout }
})
