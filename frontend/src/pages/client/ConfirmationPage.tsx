import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'

interface BookingResult {
  appointment_id: number
  payment_link: string
  message: string
}

export default function ConfirmationPage() {
  const navigate = useNavigate()
  const [result, setResult] = useState<BookingResult | null>(null)

  useEffect(() => {
    const stored = sessionStorage.getItem('booking_result')
    if (!stored) { navigate('/'); return }
    setResult(JSON.parse(stored))
  }, [navigate])

  if (!result) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center space-y-6">
        <div className="flex justify-center">
          <CheckCircle className="text-green-500" size={64} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Agendamento criado!</h1>
          <p className="text-gray-500 mt-2">
            Finalize o pagamento do sinal para confirmar seu horário. Você receberá confirmação por WhatsApp e email.
          </p>
        </div>

        <a
          href={result.payment_link}
          target="_blank"
          rel="noreferrer"
          className="block w-full py-4 bg-brand-600 text-white font-bold rounded-2xl shadow hover:bg-brand-700 transition-colors text-lg"
        >
          Pagar sinal agora →
        </a>

        <button
          onClick={() => navigate('/')}
          className="text-sm text-gray-400 hover:text-gray-600"
        >
          Voltar ao início
        </button>
      </div>
    </div>
  )
}
