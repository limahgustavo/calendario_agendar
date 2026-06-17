import { Routes, Route, Navigate } from 'react-router-dom'
import RoleGuard from '@/components/RoleGuard'

import HomePage from '@/pages/HomePage'
import LoginPage from '@/pages/auth/LoginPage'
import RegistroPage from '@/pages/auth/RegistroPage'
import StudioRegistroPage from '@/pages/auth/StudioRegistroPage'
import CriarSenhaPage from '@/pages/auth/CriarSenhaPage'
import RecuperarSenhaPage from '@/pages/auth/RecuperarSenhaPage'
import RedefinirSenhaPage from '@/pages/auth/RedefinirSenhaPage'

import BookingPage from '@/pages/public/BookingPage'
import BookingDadosPage from '@/pages/public/BookingDadosPage'
import ConfirmacaoPage from '@/pages/public/ConfirmacaoPage'
import PagamentoPendentePage from '@/pages/public/PagamentoPendentePage'
import ActionPage from '@/pages/public/ActionPage'
import AvaliarPage from '@/pages/public/AvaliarPage'

import ClienteLayout from '@/pages/cliente/ClienteLayout'
import ClienteAgendamentosPage from '@/pages/cliente/AgendamentosPage'
import ClientePerfilPage from '@/pages/cliente/PerfilPage'

import StudioLayout from '@/pages/studio/StudioLayout'
import StudioDashboardPage from '@/pages/studio/DashboardPage'
import StudioAgendamentosPage from '@/pages/studio/AgendamentosPage'
import StudioNovoAgendamentoPage from '@/pages/studio/NovoAgendamentoPage'
import StudioDisponibilidadePage from '@/pages/studio/DisponibilidadePage'
import StudioServicosPage from '@/pages/studio/ServicosPage'
import StudioLinkQRPage from '@/pages/studio/LinkQRPage'
import StudioPlanoPage from '@/pages/studio/PlanoPage'
import StudioDadosBancariosPage from '@/pages/studio/DadosBancariosPage'
import StudioRelatorioPage from '@/pages/studio/RelatorioPage'

import AdminLayout from '@/pages/admin/AdminLayout'
import AdminDashboardPage from '@/pages/admin/DashboardPage'
import AdminClientesPage from '@/pages/admin/ClientesPage'
import AdminStudiosPage from '@/pages/admin/StudiosPage'
import AdminRepassesPage from '@/pages/admin/RepassesPage'
import AdminConfiguracoesPage from '@/pages/admin/ConfiguracoesPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />

      {/* Auth */}
      <Route path="/auth/login" element={<LoginPage />} />
      <Route path="/auth/registro" element={<RegistroPage />} />
      <Route path="/auth/studio" element={<StudioRegistroPage />} />
      <Route path="/auth/criar-senha/:token" element={<CriarSenhaPage />} />
      <Route path="/auth/recuperar" element={<RecuperarSenhaPage />} />
      <Route path="/auth/redefinir/:token" element={<RedefinirSenhaPage />} />

      {/* Booking público */}
      <Route path="/booking/:slug" element={<BookingPage />} />
      <Route path="/booking/:slug/dados" element={<BookingDadosPage />} />
      <Route path="/confirmacao/:id" element={<ConfirmacaoPage />} />
      <Route path="/pagamento-pendente" element={<PagamentoPendentePage />} />
      <Route path="/acao/:token/:action" element={<ActionPage />} />
      <Route path="/avaliar/:token" element={<AvaliarPage />} />

      {/* Painel Cliente */}
      <Route
        path="/app"
        element={
          <RoleGuard allow={['cliente', 'nail_designer', 'admin']}>
            <ClienteLayout />
          </RoleGuard>
        }
      >
        <Route index element={<ClienteAgendamentosPage />} />
        <Route path="perfil" element={<ClientePerfilPage />} />
      </Route>

      {/* Painel Studio */}
      <Route
        path="/studio"
        element={
          <RoleGuard allow={['nail_designer']}>
            <StudioLayout />
          </RoleGuard>
        }
      >
        <Route index element={<StudioDashboardPage />} />
        <Route path="agendamentos" element={<StudioAgendamentosPage />} />
        <Route path="novo" element={<StudioNovoAgendamentoPage />} />
        <Route path="disponibilidade" element={<StudioDisponibilidadePage />} />
        <Route path="servicos" element={<StudioServicosPage />} />
        <Route path="link" element={<StudioLinkQRPage />} />
        <Route path="plano" element={<StudioPlanoPage />} />
        <Route path="dados-bancarios" element={<StudioDadosBancariosPage />} />
        <Route path="relatorio" element={<StudioRelatorioPage />} />
      </Route>

      {/* Painel Admin */}
      <Route
        path="/admin"
        element={
          <RoleGuard allow={['admin']}>
            <AdminLayout />
          </RoleGuard>
        }
      >
        <Route index element={<AdminDashboardPage />} />
        <Route path="clientes" element={<AdminClientesPage />} />
        <Route path="studios" element={<AdminStudiosPage />} />
        <Route path="repasses" element={<AdminRepassesPage />} />
        <Route path="configuracoes" element={<AdminConfiguracoesPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
