import { useState, useEffect } from 'react'
import { authApi } from '@/api/auth'

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(
    !!localStorage.getItem('token'),
  )

  async function login(email: string, password: string): Promise<void> {
    const { access_token } = await authApi.login(email, password)
    localStorage.setItem('token', access_token)
    setIsAuthenticated(true)
  }

  function logout() {
    localStorage.removeItem('token')
    setIsAuthenticated(false)
  }

  return { isAuthenticated, login, logout }
}
