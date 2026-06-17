import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

export default function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string
  subtitle?: string
  children: ReactNode
  footer?: ReactNode
}) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4 py-10">
      <div className="max-w-md w-full">
        <Link to="/" className="block text-center text-2xl font-bold text-brand-700 mb-6">
          💅 NailBook
        </Link>
        <div className="bg-white rounded-2xl shadow-lg p-8 space-y-5">
          <div>
            <h1 className="text-xl font-bold text-gray-800">{title}</h1>
            {subtitle && <p className="text-gray-500 text-sm mt-1">{subtitle}</p>}
          </div>
          {children}
        </div>
        {footer && <div className="text-center text-sm text-gray-500 mt-4">{footer}</div>}
      </div>
    </div>
  )
}
