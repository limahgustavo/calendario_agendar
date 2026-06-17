import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api/dashboard'
import { formatCurrency, formatDateTime, STATUS_LABELS, STATUS_COLORS } from '@/lib/utils'
import { CalendarCheck, TrendingUp, Clock, DollarSign } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardApi.summary,
    refetchInterval: 60_000,
  })

  if (isLoading) return <div className="animate-pulse text-gray-400">Carregando...</div>
  if (!data) return null

  const m = data.current_month

  const cards = [
    { label: 'Hoje', value: data.today_appointments, icon: CalendarCheck, color: 'bg-blue-50 text-blue-700' },
    { label: 'Próximos 7 dias', value: data.week_appointments, icon: Clock, color: 'bg-purple-50 text-purple-700' },
    { label: 'Receita confirmada', value: formatCurrency(m.revenue_confirmed), icon: DollarSign, color: 'bg-green-50 text-green-700' },
    { label: 'A receber (local)', value: formatCurrency(m.revenue_pending), icon: TrendingUp, color: 'bg-yellow-50 text-yellow-700' },
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-0.5">{m.month_year.replace('-', '/')}</p>
      </div>

      {/* Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
            <div className={cn('w-10 h-10 rounded-xl flex items-center justify-center mb-3', color)}>
              <Icon size={20} />
            </div>
            <div className="text-xl font-bold text-gray-800">{value}</div>
            <div className="text-sm text-gray-500 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Month stats */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h2 className="font-semibold text-gray-700 mb-4">Resumo do mês</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Total', value: m.total_appointments },
            { label: 'Confirmados', value: m.confirmed_appointments },
            { label: 'Concluídos', value: m.completed_appointments },
            { label: 'Cancelados', value: m.cancelled_appointments },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <div className="text-3xl font-bold text-brand-600">{value}</div>
              <div className="text-sm text-gray-500">{label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming */}
      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h2 className="font-semibold text-gray-700 mb-4">Próximos agendamentos</h2>
        {data.upcoming.length === 0 ? (
          <p className="text-gray-400 text-sm">Nenhum agendamento próximo.</p>
        ) : (
          <div className="divide-y">
            {data.upcoming.map((a) => (
              <div key={a.id} className="py-3 flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-800">{a.client_name}</div>
                  <div className="text-sm text-gray-500">{a.service_name} · {formatDateTime(a.scheduled_at)}</div>
                </div>
                <span className={cn('px-2.5 py-1 rounded-full text-xs font-medium', STATUS_COLORS[a.status])}>
                  {STATUS_LABELS[a.status]}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
