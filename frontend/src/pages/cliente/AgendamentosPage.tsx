import { useQuery } from '@tanstack/react-query'
import { appointmentsApi } from '@/api/appointments'
import { Button, Card, Badge, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency, formatDateShort, STATUS_LABELS, STATUS_COLORS } from '@/lib/utils'
import type { Appointment } from '@/types'

function AppointmentCard({ appointment }: { appointment: Appointment }) {
  const invoiceUrl = appointment.payment?.asaas_invoice_url
  return (
    <Card className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="space-y-1">
        <p className="font-bold text-gray-800">{appointment.studio_name ?? 'Studio'}</p>
        <p className="text-gray-600">{appointment.servico_nome}</p>
        <p className="text-sm text-gray-500">
          {formatDateShort(appointment.data)} às {appointment.hora}
        </p>
      </div>
      <div className="flex flex-col items-start gap-2 sm:items-end">
        <Badge className={STATUS_COLORS[appointment.status]}>
          {STATUS_LABELS[appointment.status]}
        </Badge>
        <p className="font-semibold text-brand-600">{formatCurrency(appointment.preco)}</p>
        {appointment.status === 'agendado' && invoiceUrl && (
          <a href={invoiceUrl} target="_blank" rel="noreferrer">
            <Button>Pagar agora</Button>
          </a>
        )}
        {appointment.payment?.status === 'confirmed' && (
          <Button variant="secondary" onClick={() => appointmentsApi.comprovante(appointment.id)}>
            Baixar comprovante
          </Button>
        )}
      </div>
    </Card>
  )
}

export default function AgendamentosPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['client-appointments'],
    queryFn: appointmentsApi.clientList,
  })

  const today = new Date().toISOString().slice(0, 10)

  const proximos = (data ?? []).filter(
    (a) => (a.status === 'agendado' || a.status === 'confirmado') && a.data >= today,
  )
  const historico = (data ?? []).filter((a) => !proximos.includes(a))

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Meus agendamentos</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && (data ?? []).length === 0 && (
        <p className="text-gray-500">Você ainda não tem agendamentos.</p>
      )}

      {!isLoading && !isError && (data ?? []).length > 0 && (
        <>
          <section className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-700">Próximos</h2>
            {proximos.length === 0 ? (
              <p className="text-gray-500">Nenhum agendamento próximo.</p>
            ) : (
              proximos.map((a) => <AppointmentCard key={a.id} appointment={a} />)
            )}
          </section>

          <section className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-700">Histórico</h2>
            {historico.length === 0 ? (
              <p className="text-gray-500">Nenhum agendamento no histórico.</p>
            ) : (
              historico.map((a) => <AppointmentCard key={a.id} appointment={a} />)
            )}
          </section>
        </>
      )}
    </div>
  )
}
