import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CheckCircle, XCircle, RefreshCw } from 'lucide-react'
import { appointmentsApi } from '@/api/appointments'
import { Button, Spinner } from '@/components/ui'

const CONFIG: Record<string, { fn: (t: string) => Promise<unknown>; icon: typeof CheckCircle; color: string }> = {
  confirmar: { fn: appointmentsApi.confirmByToken, icon: CheckCircle, color: 'text-green-500' },
  cancelar: { fn: appointmentsApi.cancelByToken, icon: XCircle, color: 'text-red-500' },
  remarcar: { fn: appointmentsApi.rescheduleByToken, icon: RefreshCw, color: 'text-brand-500' },
}

export default function ActionPage() {
  const { token = '', action = '' } = useParams()
  const navigate = useNavigate()
  const [state, setState] = useState<'loading' | 'ok' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const cfg = CONFIG[action]
    if (!cfg) {
      setState('error')
      setMessage('Ação inválida.')
      return
    }
    cfg
      .fn(token)
      .then((res) => {
        setState('ok')
        setMessage((res as { message?: string })?.message || 'Feito!')
      })
      .catch((e) => {
        setState('error')
        setMessage(e?.response?.data?.detail || 'Não foi possível processar.')
      })
  }, [token, action])

  if (state === 'loading') return <Spinner />

  const cfg = CONFIG[action]
  const Icon = state === 'ok' && cfg ? cfg.icon : XCircle
  const color = state === 'ok' && cfg ? cfg.color : 'text-red-500'

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center space-y-6">
        <Icon className={`mx-auto ${color}`} size={64} />
        <p className="text-lg text-gray-700">{message}</p>
        <Button onClick={() => navigate('/')} className="w-full">
          Voltar ao início
        </Button>
      </div>
    </div>
  )
}
