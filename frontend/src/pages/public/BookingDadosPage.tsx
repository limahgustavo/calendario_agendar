import { useState, type FormEvent } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { appointmentsApi } from '@/api/appointments'
import { Button, Input, Field, ErrorMessage } from '@/components/ui'
import { formatCurrency, formatDate } from '@/lib/utils'
import type { Service, StudioPublic } from '@/types'

interface Draft {
  service: Service
  date: string
  time_str: string
  studio: StudioPublic
}

export default function BookingDadosPage() {
  const { slug = '' } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  const draft = location.state as Draft | null

  const [form, setForm] = useState({
    client_name: '',
    client_email: '',
    client_phone: '',
    client_cpf_cnpj: '',
  })

  const mutation = useMutation({
    mutationFn: () => {
      if (!draft) throw new Error('Dados do agendamento perdidos. Volte e selecione novamente.')
      return appointmentsApi.book(slug, {
        service_id: draft.service.id,
        data: draft.date,
        hora: draft.time_str,
        ...form,
      })
    },
    onSuccess: (res) => {
      sessionStorage.setItem('booking_result', JSON.stringify(res))
      navigate(`/confirmacao/${res.appointment_id}`, { state: res })
    },
  })

  if (!draft) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-3 px-4 text-center">
        <p className="text-gray-500">Sessão de agendamento expirada.</p>
        <Button onClick={() => navigate(`/booking/${slug}`)}>Recomeçar</Button>
      </div>
    )
  }

  const total = draft.service.price
  const isFull = draft.studio.payment_mode === 'full_100'
  const amount = isFull ? total : total * 0.5

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white py-10 px-4">
      <div className="max-w-lg mx-auto space-y-6">
        <button onClick={() => navigate(-1)} className="text-brand-600 text-sm hover:underline">
          ← Voltar
        </button>
        <h1 className="text-2xl font-bold text-brand-700">Confirme seus dados</h1>

        <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm space-y-2">
          <Row label="Studio" value={draft.studio.name} />
          <Row label="Serviço" value={draft.service.name} />
          <Row label="Data" value={formatDate(draft.date)} />
          <Row label="Horário" value={draft.time_str} />
          <div className="border-t pt-2 flex justify-between">
            <span className="text-gray-500 text-sm">Valor total</span>
            <span className="font-bold">{formatCurrency(total)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-brand-600 text-sm font-medium">
              {isFull ? 'Pagamento agora (100%)' : 'Sinal agora (50%)'}
            </span>
            <span className="text-brand-700 font-bold">{formatCurrency(amount)}</span>
          </div>
          {!isFull && (
            <p className="text-xs text-gray-400">
              Os outros {formatCurrency(total - amount)} são pagos no dia, no studio.
            </p>
          )}
        </div>

        <form
          onSubmit={(e: FormEvent) => {
            e.preventDefault()
            mutation.mutate()
          }}
          className="space-y-4"
        >
          <Field label="Nome completo">
            <Input
              value={form.client_name}
              onChange={(e) => setForm({ ...form, client_name: e.target.value })}
              required
            />
          </Field>
          <Field label="Email">
            <Input
              type="email"
              value={form.client_email}
              onChange={(e) => setForm({ ...form, client_email: e.target.value })}
              required
            />
          </Field>
          <Field label="WhatsApp">
            <Input
              value={form.client_phone}
              onChange={(e) => setForm({ ...form, client_phone: e.target.value })}
              placeholder="(11) 99999-9999"
              required
            />
          </Field>
          <Field label="CPF ou CNPJ">
            <Input
              value={form.client_cpf_cnpj}
              onChange={(e) => setForm({ ...form, client_cpf_cnpj: e.target.value })}
              placeholder="000.000.000-00"
              required
            />
          </Field>

          {mutation.isError ? <ErrorMessage error={mutation.error} /> : null}

          <Button type="submit" disabled={mutation.isPending} className="w-full py-4 text-lg">
            {mutation.isPending ? 'Aguarde...' : `Pagar ${formatCurrency(amount)} →`}
          </Button>
        </form>
      </div>
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  )
}
