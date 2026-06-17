import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation } from '@tanstack/react-query'
import { appointmentsApi } from '@/api/appointments'
import type { BookingDraft } from '@/types'
import { formatCurrency, formatDate } from '@/lib/utils'

const schema = z.object({
  client_name: z.string().min(2, 'Nome muito curto'),
  client_email: z.string().email('Email inválido'),
  client_phone: z.string().min(8, 'Telefone inválido'),
  client_cpf_cnpj: z.string().min(11, 'CPF inválido (mínimo 11 dígitos)').max(18, 'CNPJ inválido'),
  notes: z.string().optional(),
})

type FormData = z.infer<typeof schema>

export default function BookingPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [draft, setDraft] = useState<BookingDraft | null>(null)

  useEffect(() => {
    const state = location.state as BookingDraft | null
    if (!state?.service || !state.date || !state.time_str) { navigate('/'); return }
    setDraft(state)
  }, [location.state, navigate])

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) => {
      if (!draft?.service || !draft.date || !draft.time_str) throw new Error('Dados do agendamento perdidos. Volte e selecione novamente.')
      const scheduled_at = `${draft.date}T${draft.time_str}:00`
      return appointmentsApi.create({
        service_id: draft.service.id,
        scheduled_at,
        ...data,
      })
    },
    onSuccess: (res) => {
      sessionStorage.removeItem('booking')
      sessionStorage.setItem('booking_result', JSON.stringify(res))
      navigate(`/confirmacao/${res.appointment_id}`, { state: res })
    },
  })

  if (!draft) return null

  const deposit = draft.service ? draft.service.price * 0.5 : 0
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const errorMsg = mutation.isError ? ((mutation.error as any)?.response?.data?.detail || (mutation.error as Error)?.message || 'Erro ao criar agendamento.') : null

  const fields = [
    { name: 'client_name', label: 'Nome completo', type: 'text', placeholder: 'Seu nome' },
    { name: 'client_email', label: 'Email', type: 'email', placeholder: 'seu@email.com' },
    { name: 'client_phone', label: 'WhatsApp', type: 'tel', placeholder: '(11) 99999-9999' },
    { name: 'client_cpf_cnpj', label: 'CPF ou CNPJ', type: 'text', placeholder: '000.000.000-00' },
  ] as const

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white py-10 px-4">
      <div className="max-w-lg mx-auto space-y-6">
        <button onClick={() => navigate('/')} className="text-brand-600 text-sm hover:underline">
          ← Voltar
        </button>

        <h1 className="text-2xl font-bold text-brand-700">Confirme seus dados</h1>

        {/* Booking summary */}
        <div className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Serviço</span>
            <span className="font-medium">{draft.service?.name}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Data</span>
            <span className="font-medium">{draft.date ? formatDate(draft.date) : ''}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Horário</span>
            <span className="font-medium">{draft.time_str}</span>
          </div>
          <div className="border-t pt-2 flex justify-between">
            <span className="text-gray-500 text-sm">Total</span>
            <span className="font-bold">{formatCurrency(draft.service?.price ?? 0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-brand-600 text-sm font-medium">Sinal hoje (50%)</span>
            <span className="text-brand-700 font-bold">{formatCurrency(deposit)}</span>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="space-y-4">
          {fields.map(({ name, label, type, placeholder }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input
                type={type}
                placeholder={placeholder}
                {...register(name)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-400"
              />
              {errors[name] && (
                <p className="text-red-500 text-xs mt-1">{errors[name]?.message}</p>
              )}
            </div>
          ))}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Observações (opcional)</label>
            <textarea
              {...register('notes')}
              rows={3}
              placeholder="Alguma observação..."
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-400 resize-none"
            />
          </div>

          {errorMsg && (
            <p className="text-red-500 text-sm bg-red-50 border border-red-200 rounded-xl p-3">{errorMsg}</p>
          )}

          <button
            type="submit"
            disabled={mutation.isPending}
            className="w-full py-4 bg-brand-600 text-white font-bold rounded-2xl shadow hover:bg-brand-700 disabled:opacity-50 transition-colors text-lg"
          >
            {mutation.isPending ? 'Aguarde...' : `Pagar sinal ${formatCurrency(deposit)} →`}
          </button>
        </form>
      </div>
    </div>
  )
}
