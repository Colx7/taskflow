import request from '@/utils/request'

export interface LoginParams {
  username: string
  password: string
}

export interface RegisterParams {
  username: string
  email: string
  password: string
}

export interface TokenData {
  user: {
    id: number
    username: string
    email: string
    avatar_url: string | null
    created_at: string | null
  }
  token: string
}

// 登录
export const login = (data: LoginParams) => {
  return request.post('/auth/login', data) as Promise<TokenData>
}

// 注册
export const register = (data: RegisterParams) => {
  return request.post('/auth/register', data) as Promise<TokenData>
}

// 获取当前用户信息
export const getMe = () => {
  return request.get('/auth/me') as Promise<{ id: number; username: string; email: string; avatar_url: string | null; created_at: string | null }>
}
