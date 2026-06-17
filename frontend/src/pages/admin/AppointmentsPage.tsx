import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { appointmentsApi } from '@/api/appointments'
import type { AppointmentStatus } from '@/types'
import { formatCurrency, formatDateTime, STATUS_LABELS, STATUS_COLORS, cn } from '@/lib/utils'

const STATUSES: Array<{ value: AppointmentStatus | ''; label: string }> = [
  { value: '', label: 'Todos' },
  { value: 'pending_payment', label: 'Aguardando pagamento' },
  { value: 'confirmed', label: 'Confirmados' },
  { value: 'completed', label: 'Concluídos' },
  { value: 'cancelled', label: 'Cancelados' },
]

export default function AppointmentsPage() {
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState<AppointmentStatus | ''>('')
  const [monthYear, setMonthYear] = useState(format(new Date(), 'yyyy-MM'))

  const { data: appointments = [], isLoading } = useQuery({
    queryKey: ['appointments', statusFilter, monthYear],
    queryFn: () =>
      appointmentsApi.list({
        status: statusFilter || undefined,
        month_year: monthYear,
      }),
  })

  const complete = useMutation({
    mutationFn: (id: number) => appointmentsApi.update(id, { status: 'completed' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['appointments'] }),
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Agendamentos</h1>
        <input
          type="month"
          value={monthYear}
          onChange={(e) => setMonthYear(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-400"
        />
      </div>

      {/* Status filter */}
      <div className="flex gap-2 flex-wrap">
        {STATUSES.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => setStatusFilter(value as AppointmentStatus | '')}
            className={cn(
              'px-4 py-1.5 rounded-full text-sm font-medium border transition-colors',
              statusFilter === value
                ? 'bg-brand-600 text-white border-brand-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-brand-300',
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">Carregando...</div>
        ) : appointments.length === 0 ? (
          <div className="p-8 text-center text-gray-400">Nenhum agendamento encontrado.</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
              <tr>
                {['Cliente', 'Serviço', 'Data/hora', 'Sinal', 'Status', 'Ações'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {appointments.map((a) => (
                <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{a.client_name}</div>
                    <div className="text-xs text-gray-400">{a.client_phone}</div>
                  </td>
                  <td className="px-4 py-3">{a.service.name}</td>
                  <td className="px-4 py-3 whitespace-nowrap">{formatDateTime(a.scheduled_at)}</td>
                  <td className="px-4 py-3">
                    {a.payment ? (
                      <span className={cn(
                        'px-2 py-0.5 rounded-full text-xs',
                        a.payment.status === 'confirmed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700',
                      )}>
                        {formatCurrency(a.payment.amount)}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn('px-2.5 py-1 rounded-full text-xs font-medium', STATUS_COLORS[a.status])}>
                      {STATUS_LABELS[a.status]}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    {a.status === 'confirmed' && (
                      <button
                        onClick={() => complete.mutate(a.id)}
                        disabled={complete.isPending}
                        className="text-xs px-3 py-1.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50"
                      >
                        Concluir
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
