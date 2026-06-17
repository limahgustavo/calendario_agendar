import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'
import type { UserRole } from '@/types'
import { homeForRole } from '@/hooks/useAuth'

export default function RoleGuard({
  allow,
  children,
}: {
  allow: UserRole[]
  children: ReactNode
}) {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role') as UserRole | null

  if (!token) return <Navigate to="/auth/login" replace />
  if (role && !allow.includes(role)) return <Navigate to={homeForRole(role)} replace />
  return <>{children}</>
}
