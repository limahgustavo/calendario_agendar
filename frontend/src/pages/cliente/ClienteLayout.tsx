import { CalendarHeart, User } from 'lucide-react'
import DashboardLayout from '@/components/DashboardLayout'

export default function ClienteLayout() {
  return (
    <DashboardLayout
      title="💅 NailBook"
      items={[
        { to: '/app', label: 'Meus agendamentos', icon: CalendarHeart, end: true },
        { to: '/app/perfil', label: 'Perfil', icon: User },
      ]}
    />
  )
}
