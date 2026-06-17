import { Link } from 'react-router-dom'
import { CalendarHeart, Store, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white">
      <header className="max-w-5xl mx-auto px-4 h-16 flex items-center justify-between">
        <span className="text-xl font-bold text-brand-700">💅 NailBook</span>
        <Link to="/auth/login">
          <Button variant="secondary">Entrar</Button>
        </Link>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-16 text-center">
        <div className="inline-flex items-center gap-2 bg-brand-100 text-brand-700 px-3 py-1 rounded-full text-sm font-medium mb-6">
          <Sparkles size={15} /> Agendamento para nail designers
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 leading-tight">
          Sua agenda, pagamentos e clientes <span className="text-brand-600">num só lugar</span>
        </h1>
        <p className="text-gray-500 mt-4 max-w-xl mx-auto">
          Clientes agendam e pagam online. Você controla horários, recebe os repasses e envia
          lembretes automáticos por WhatsApp.
        </p>

        <div className="grid sm:grid-cols-2 gap-4 mt-12 max-w-2xl mx-auto">
          <Link
            to="/auth/studio"
            className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6 text-left hover:shadow-md transition-shadow"
          >
            <Store className="text-brand-600" size={28} />
            <h2 className="font-bold text-gray-800 mt-3">Sou nail designer</h2>
            <p className="text-gray-500 text-sm mt-1">
              Cadastre seu studio, configure horários e gere seu link de agendamento.
            </p>
            <span className="text-brand-600 font-medium text-sm mt-3 inline-block">
              Cadastrar studio →
            </span>
          </Link>

          <Link
            to="/auth/registro"
            className="bg-white border border-gray-100 rounded-2xl shadow-sm p-6 text-left hover:shadow-md transition-shadow"
          >
            <CalendarHeart className="text-brand-600" size={28} />
            <h2 className="font-bold text-gray-800 mt-3">Sou cliente</h2>
            <p className="text-gray-500 text-sm mt-1">
              Crie sua conta para acompanhar seus agendamentos em todos os studios.
            </p>
            <span className="text-brand-600 font-medium text-sm mt-3 inline-block">
              Criar conta →
            </span>
          </Link>
        </div>

        <p className="text-gray-400 text-sm mt-10">
          Recebeu um link de um studio? É só abrir para agendar — não precisa de conta.
        </p>
      </main>
    </div>
  )
}
