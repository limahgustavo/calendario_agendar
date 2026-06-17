export interface Service {
  id: number
  name: string
  description: string | null
  price: number
  duration_minutes: number
  is_active: boolean
}

export interface CalendarSlot {
  date: string       // YYYY-MM-DD
  time_str: string   // HH:MM
  available: boolean
}

export type AppointmentStatus =
  | 'pending_payment'
  | 'confirmed'
  | 'completed'
  | 'cancelled'
  | 'rescheduled'

export interface PaymentSummary {
  id: number
  amount: number
  status: string
  asaas_payment_link: string | null
}

export interface Appointment {
  id: number
  service: Service
  client_name: string
  client_email: string
  client_phone: string
  scheduled_at: string
  status: AppointmentStatus
  notes: string | null
  payment: PaymentSummary | null
  reminder_24h_sent: boolean
  reminder_2h_sent: boolean
  client_confirmed_at: string | null
  created_at: string
}

export interface BookingDraft {
  service: Service | null
  date: string | null        // YYYY-MM-DD
  time_str: string | null    // HH:MM
}

export interface RevenueSummary {
  month_year: string
  total_appointments: number
  confirmed_appointments: number
  completed_appointments: number
  cancelled_appointments: number
  revenue_confirmed: number
  revenue_pending: number
}

export interface DashboardSummary {
  today_appointments: number
  week_appointments: number
  current_month: RevenueSummary
  upcoming: Array<{
    id: number
    client_name: string
    service_name: string
    scheduled_at: string
    status: AppointmentStatus
  }>
}
