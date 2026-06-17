import { useState } from 'react'
import { authApi } from '@/api/auth'
import type { UserRole } from '@/types'

export function useAuth() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [role, setRole] = useState<UserRole | null>(
    localStorage.getItem('role') as UserRole | null,
  )

  function setSession(access_token: string, r: UserRole) {
    localStorage.setItem('token', access_token)
    localStorage.setItem('role', r)
    setToken(access_token)
    setRole(r)
  }

  async function login(email: string, password: string): Promise<UserRole> {
    const res = await authApi.login(email, password)
    setSession(res.access_token, res.role)
    return res.role
  }

  function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    setToken(null)
    setRole(null)
  }

  return { token, role, isAuthenticated: !!token, login, setSession, logout }
}

export function homeForRole(role: UserRole | null): string {
  if (role === 'admin') return '/admin'
  if (role === 'nail_designer') return '/studio'
  return '/app'
}
