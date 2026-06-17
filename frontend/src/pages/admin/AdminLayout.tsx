import { LayoutDashboard, Users, Store, Banknote, Settings } from 'lucide-react'
import DashboardLayout from '@/components/DashboardLayout'

export default function AdminLayout() {
  return (
    <DashboardLayout
      title="⚙️ Admin"
      items={[
        { to: '/admin', label: 'Dashboard', icon: LayoutDashboard, end: true },
        { to: '/admin/clientes', label: 'Clientes', icon: Users },
        { to: '/admin/studios', label: 'Studios', icon: Store },
        { to: '/admin/repasses', label: 'Repasses', icon: Banknote },
        { to: '/admin/configuracoes', label: 'Configurações', icon: Settings },
      ]}
    />
  )
}
