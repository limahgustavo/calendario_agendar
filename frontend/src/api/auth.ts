import api from './client'
import type { User, UserRole } from '@/types'

interface TokenResponse {
  access_token: string
  token_type: string
  role: UserRole
}

export const authApi = {
  register: (data: { name: string; email: string; whatsapp?: string; celular?: string }) =>
    api.post('/auth/register', data).then((r) => r.data),

  setPassword: (token: string, password: string) =>
    api.post<TokenResponse>('/auth/set-password', { token, password }).then((r) => r.data),

  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }).then((r) => r.data),

  forgotPassword: (email: string) =>
    api.post('/auth/forgot-password', { email }).then((r) => r.data),

  resetPassword: (token: string, password: string) =>
    api.post<TokenResponse>('/auth/reset-password', { token, password }).then((r) => r.data),

  me: () => api.get<User>('/auth/me').then((r) => r.data),

  updateMe: (data: Partial<Pick<User, 'name' | 'whatsapp' | 'celular' | 'cpf_cnpj'>>) =>
    api.put<User>('/auth/me', data).then((r) => r.data),
}
