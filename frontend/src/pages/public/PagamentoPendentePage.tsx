import { useNavigate } from 'react-router-dom'
import { Clock } from 'lucide-react'
import { Button } from '@/components/ui'

export default function PagamentoPendentePage() {
  const navigate = useNavigate()
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center space-y-6">
        <Clock className="text-yellow-500 mx-auto" size={64} />
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Pagamento pendente</h1>
          <p className="text-gray-500 mt-2">
            Seu agendamento foi criado! O link de pagamento será enviado por WhatsApp e email em
            breve.
          </p>
        </div>
        <Button onClick={() => navigate('/')} className="w-full">
          Voltar ao início
        </Button>
      </div>
    </div>
  )
}
