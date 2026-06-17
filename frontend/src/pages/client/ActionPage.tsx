import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { appointmentsApi } from '@/api/appointments'
import { CheckCircle, XCircle, RefreshCw, Loader2 } from 'lucide-react'

type ActionType = 'confirmar' | 'cancelar' | 'remarcar'

const CONFIG: Record<ActionType, { label: string; icon: React.ReactNode; color: string }> = {
  confirmar: { label: 'Agendamento confirmado!', icon: <CheckCircle size={64} className="text-green-500" />, color: 'text-green-700' },
  cancelar: { label: 'Agendamento cancelado.', icon: <XCircle size={64} className="text-red-500" />, color: 'text-red-700' },
  remarcar: { label: 'Solicitação de remarcação enviada!', icon: <RefreshCw size={64} className="text-blue-500" />, color: 'text-blue-700' },
}

export default function ActionPage() {
  const { token, action } = useParams<{ token: string; action: ActionType }>()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    if (!token || !action) return
    const fn =
      action === 'confirmar' ? appointmentsApi.confirmByToken :
      action === 'cancelar' ? appointmentsApi.cancelByToken :
      appointmentsApi.rescheduleByToken

    fn(token)
      .then((r) => { setMessage(r.message); setStatus('success') })
      .catch((e) => { setMessage(e.response?.data?.detail ?? 'Erro inesperado.'); setStatus('error') })
  }, [token, action])

  const cfg = action ? CONFIG[action as ActionType] : null

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center space-y-6">
        {status === 'loading' && (
          <Loader2 className="mx-auto animate-spin text-brand-500" size={48} />
        )}
        {status === 'success' && cfg && (
          <>
            <div className="flex justify-center">{cfg.icon}</div>
            <h1 className={`text-xl font-bold ${cfg.color}`}>{message || cfg.label}</h1>
            <a href="/" className="text-sm text-brand-600 hover:underline">Fazer novo agendamento</a>
          </>
        )}
        {status === 'error' && (
          <>
            <XCircle className="mx-auto text-red-400" size={48} />
            <h1 className="text-xl font-bold text-red-600">{message}</h1>
            <a href="/" className="text-sm text-brand-600 hover:underline">Voltar ao início</a>
          </>
        )}
      </div>
    </div>
  )
}
