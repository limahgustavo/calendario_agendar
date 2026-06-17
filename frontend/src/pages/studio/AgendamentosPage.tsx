import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { appointmentsApi } from '@/api/appointments'
import { Button, Card, Badge, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency, formatDateShort, STATUS_LABELS, STATUS_COLORS, cn } from '@/lib/utils'
import type { Appointment, AppointmentStatus } from '@/types'

type Filter =
  | { key: 'todos'; label: 'Todos' }
  | { key: 'pendentes'; label: 'Pendentes' }
  | { key: AppointmentStatus; label: string }

const FILTERS: Filter[] = [
  { key: 'todos', label: 'Todos' },
  { key: 'pendentes', label: 'Pendentes' },
  { key: 'agendado', label: STATUS_LABELS.agendado },
  { key: 'confirmado', label: STATUS_LABELS.confirmado },
  { key: 'realizado', label: STATUS_LABELS.realizado },
  { key: 'cancelado', label: STATUS_LABELS.cancelado },
]

function AppointmentCard({ appointment }: { appointment: Appointment }) {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: () => appointmentsApi.update(appointment.id, { status: 'realizado' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['studio-appointments'] })
    },
  })

  return (
    <Card className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="space-y-1">
        <p className="font-bold text-gray-800">{appointment.client_name}</p>
        <p className="text-sm text-gray-500">{appointment.client_email}</p>
        <p className="text-sm text-gray-500">{appointment.client_phone}</p>
        <p className="text-gray-600">{appointment.servico_nome}</p>
        <p className="text-sm text-gray-500">
          {formatDateShort(appointment.data)} {appointment.hora}
        </p>
      </div>
      <div className="flex flex-col items-start gap-2 sm:items-end">
        <Badge className={STATUS_COLORS[appointment.status]}>
          {STATUS_LABELS[appointment.status]}
        </Badge>
        <p className="font-semibold text-brand-600">{formatCurrency(appointment.preco)}</p>
        {appointment.status === 'confirmado' && (
          <Button
            variant="secondary"
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
          >
            {mutation.isPending ? 'Aguarde...' : 'Marcar realizado'}
          </Button>
        )}
        {mutation.isError && <ErrorMessage error={mutation.error} />}
      </div>
    </Card>
  )
}

export default function AgendamentosPage() {
  const [filter, setFilter] = useState<Filter['key']>('todos')

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['studio-appointments', filter],
    queryFn: () => {
      if (filter === 'todos') return appointmentsApi.studioList()
      if (filter === 'pendentes') return appointmentsApi.studioList({ pendentes: true })
      return appointmentsApi.studioList({ status: filter })
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-bold text-gray-800">Agendamentos</h1>
        <Link to="/studio/novo">
          <Button>+ Novo agendamento</Button>
        </Link>
      </div>

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={cn(
              'px-4 py-1.5 rounded-full text-sm font-medium transition-colors',
              filter === f.key
                ? 'bg-brand-600 text-white'
                : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50',
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && (data ?? []).length === 0 && (
        <p className="text-gray-500">Nenhum agendamento encontrado.</p>
      )}

      {!isLoading && !isError && (data ?? []).length > 0 && (
        <div className="space-y-3">
          {(data ?? []).map((a) => (
            <AppointmentCard key={a.id} appointment={a} />
          ))}
        </div>
      )}
    </div>
  )
}
