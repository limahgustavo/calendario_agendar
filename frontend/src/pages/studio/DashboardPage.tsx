import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '@/api/dashboard'
import { Card, Badge, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency, formatDateShort, STATUS_LABELS, STATUS_COLORS } from '@/lib/utils'
import type { Appointment } from '@/types'

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-800">{value}</p>
    </Card>
  )
}

function ProximoCard({ appointment }: { appointment: Appointment }) {
  return (
    <Card className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="space-y-1">
        <p className="font-bold text-gray-800">{appointment.client_name}</p>
        <p className="text-gray-600">{appointment.servico_nome}</p>
        <p className="text-sm text-gray-500">
          {formatDateShort(appointment.data)} às {appointment.hora}
        </p>
      </div>
      <Badge className={STATUS_COLORS[appointment.status]}>
        {STATUS_LABELS[appointment.status]}
      </Badge>
    </Card>
  )
}

export default function DashboardPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['studio-dashboard'],
    queryFn: dashboardApi.studio,
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Dashboard</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Recebido no mês" value={formatCurrency(data.faturamento_mes_recebido)} />
            <StatCard
              label="A receber (presencial)"
              value={formatCurrency(data.faturamento_mes_a_receber)}
            />
            <StatCard label="Agendamentos no mês" value={data.total_mes} />
            <StatCard label="Pendentes" value={data.pendentes_count} />
          </div>

          <section className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-700">Próximos agendamentos</h2>
            {data.proximos.length === 0 ? (
              <p className="text-gray-500">Nenhum agendamento próximo.</p>
            ) : (
              data.proximos.map((a) => <ProximoCard key={a.id} appointment={a} />)
            )}
          </section>
        </>
      )}
    </div>
  )
}
