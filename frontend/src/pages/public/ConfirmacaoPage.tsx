import { useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui'
import { formatCurrency } from '@/lib/utils'
import type { BookingResponse } from '@/types'

export default function ConfirmacaoPage() {
  const location = useLocation()
  const navigate = useNavigate()

  const stored = sessionStorage.getItem('booking_result')
  const result: BookingResponse | null =
    (location.state as BookingResponse | null) || (stored ? JSON.parse(stored) : null)

  useEffect(() => {
    if (!result) navigate('/')
    else sessionStorage.removeItem('booking_result')
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (!result) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center space-y-6">
        <CheckCircle className="text-green-500 mx-auto" size={64} />
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Agendamento criado!</h1>
          <p className="text-gray-500 mt-2">
            Finalize o pagamento de <strong>{formatCurrency(result.amount)}</strong> para confirmar.
            Você receberá a confirmação por WhatsApp e email.
          </p>
        </div>
        <a href={result.payment_link} target="_blank" rel="noreferrer" className="block">
          <Button className="w-full py-4 text-lg">Pagar agora →</Button>
        </a>
        <button onClick={() => navigate('/')} className="text-sm text-gray-400 hover:text-gray-600">
          Voltar ao início
        </button>
      </div>
    </div>
  )
}
