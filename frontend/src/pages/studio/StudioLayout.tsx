import {
  LayoutDashboard,
  CalendarDays,
  Clock,
  Scissors,
  QrCode,
  CreditCard,
  Landmark,
  BarChart3,
} from 'lucide-react'
import DashboardLayout from '@/components/DashboardLayout'

export default function StudioLayout() {
  return (
    <DashboardLayout
      title="💅 Meu Studio"
      items={[
        { to: '/studio', label: 'Dashboard', icon: LayoutDashboard, end: true },
        { to: '/studio/agendamentos', label: 'Agendamentos', icon: CalendarDays },
        { to: '/studio/disponibilidade', label: 'Disponibilidade', icon: Clock },
        { to: '/studio/servicos', label: 'Serviços', icon: Scissors },
        { to: '/studio/relatorio', label: 'Relatórios', icon: BarChart3 },
        { to: '/studio/link', label: 'Link & QR', icon: QrCode },
        { to: '/studio/plano', label: 'Plano', icon: CreditCard },
        { to: '/studio/dados-bancarios', label: 'Recebimento', icon: Landmark },
      ]}
    />
  )
}
