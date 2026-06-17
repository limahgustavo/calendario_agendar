import { Routes, Route, Navigate } from 'react-router-dom'
import CalendarPage from '@/pages/client/CalendarPage'
import BookingPage from '@/pages/client/BookingPage'
import ConfirmationPage from '@/pages/client/ConfirmationPage'
import ActionPage from '@/pages/client/ActionPage'
import PagamentoPendentePage from '@/pages/client/PagamentoPendentePage'
import LoginPage from '@/pages/admin/LoginPage'
import DashboardPage from '@/pages/admin/DashboardPage'
import AppointmentsPage from '@/pages/admin/AppointmentsPage'
import ServicesPage from '@/pages/admin/ServicesPage'
import AvailabilityPage from '@/pages/admin/AvailabilityPage'
import AdminLayout from '@/components/admin/AdminLayout'
import RequireAuth from '@/components/admin/RequireAuth'

export default function App() {
  return (
    <Routes>
      {/* Client booking flow */}
      <Route path="/" element={<CalendarPage />} />
      <Route path="/agendar" element={<BookingPage />} />
      <Route path="/confirmacao/:id" element={<ConfirmationPage />} />
      <Route path="/acao/:token/:action" element={<ActionPage />} />
      <Route path="/pagamento-pendente" element={<PagamentoPendentePage />} />

      {/* Admin */}
      <Route path="/admin/login" element={<LoginPage />} />
      <Route
        path="/admin"
        element={
          <RequireAuth>
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="agendamentos" element={<AppointmentsPage />} />
        <Route path="servicos" element={<ServicesPage />} />
        <Route path="disponibilidade" element={<AvailabilityPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
