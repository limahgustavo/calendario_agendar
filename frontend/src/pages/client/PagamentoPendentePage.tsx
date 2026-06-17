import { useNavigate } from 'react-router-dom'
import { Clock } from 'lucide-react'

export default function PagamentoPendentePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center space-y-6">
        <div className="flex justify-center">
          <Clock className="text-yellow-500" size={64} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Pagamento Pendente</h1>
          <p className="text-gray-500 mt-2">
            Seu agendamento foi criado! O link de pagamento será enviado por WhatsApp e email em breve.
          </p>
          <p className="text-gray-400 text-sm mt-3">
            Se preferir, entre em contato diretamente para finalizar o pagamento do sinal.
          </p>
        </div>

        <button
          onClick={() => navigate('/')}
          className="w-full py-3 bg-brand-600 text-white font-bold rounded-2xl shadow hover:bg-brand-700 transition-colors"
        >
          Voltar ao início
        </button>
      </div>
    </div>
  )
}
