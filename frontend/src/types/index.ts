export type UserRole = 'cliente' | 'nail_designer' | 'admin'
export type PaymentMode = 'deposit_50' | 'full_100'
export type ServiceCategory = 'aplicacao' | 'manutencao' | 'outros'
export type StudioPlan = 'basico' | 'premium' | 'pro'
export type AppointmentStatus =
  | 'agendado'
  | 'confirmado'
  | 'cancelado'
  | 'realizado'
  | 'remarcado'
export type PaymentStatus = 'pending' | 'confirmed' | 'failed' | 'refunded'
export type PaymentType = 'deposit' | 'full' | 'remainder'
export type PayoutStatus =
  | 'pendente_aprovacao'
  | 'aprovado'
  | 'transferido'
  | 'bloqueado'

export interface User {
  id: string
  name: string
  email: string
  whatsapp: string | null
  celular: string | null
  cpf_cnpj: string | null
  role: UserRole
  email_verified: boolean
}

export interface Studio {
  id: string
  name: string
  slug: string
  email: string | null
  whatsapp: string | null
  payment_mode: PaymentMode
  plano: StudioPlan
  pix_key: string | null
  bank_info: string | null
}

export interface StudioPublic {
  id: string
  name: string
  slug: string
  payment_mode: PaymentMode
  whatsapp: string | null
}

export interface Service {
  id: string
  studio_id: string
  categoria: ServiceCategory
  name: string
  description: string | null
  price: number
  duration_minutes: number
  is_active: boolean
}

export interface CalendarSlot {
  date: string // YYYY-MM-DD
  time_str: string // HH:MM
  available: boolean
}

export interface Availability {
  id: string
  studio_id: string
  ano: number
  mes: number
  dias_semana: number[]
  horarios: string[]
}

export interface PaymentInfo {
  valor: number
  tipo: PaymentType
  status: PaymentStatus
  asaas_invoice_url: string | null
}

export interface Appointment {
  id: string
  studio_id: string
  studio_name: string | null
  servico_nome: string
  preco: number
  payment_mode: PaymentMode
  data: string // YYYY-MM-DD
  hora: string // HH:MM
  scheduled_at: string
  status: AppointmentStatus
  valor_pago: number
  client_name: string
  client_email: string
  client_phone: string
  notas: string | null
  confirmado_cliente_at: string | null
  rating: number | null
  payment: PaymentInfo | null
}

export interface BookingResponse {
  appointment_id: string
  payment_link: string
  amount: number
  payment_mode: PaymentMode
  message: string
}

export interface BookingDraft {
  service: Service | null
  date: string | null
  time_str: string | null
}

export interface StudioDashboard {
  proximos: Appointment[]
  faturamento_mes_recebido: number
  faturamento_mes_a_receber: number
  total_mes: number
  confirmados_mes: number
  pendentes_count: number
}

export interface AdminDashboard {
  faturado_mes: number
  repasses_pendentes: number
  clientes_ativos: number
  studios_ativos: number
  taxa_padrao: number
}

export interface ClientRow {
  id: string
  name: string
  email: string
  whatsapp: string | null
  total_agendamentos: number
  is_active: boolean
  created_at: string
}

export interface StudioRow {
  id: string
  name: string
  slug: string
  owner_email: string | null
  plano: StudioPlan
  agendamentos_total: number
  is_active: boolean
  bank_verified: boolean
  created_at: string
}

export interface Payout {
  id: string
  studio_id: string
  studio_name: string | null
  semana_inicio: string
  valor_bruto: number
  taxa_admin_pct: number
  taxa_admin_valor: number
  valor_liquido: number
  status: PayoutStatus
  asaas_transfer_id: string | null
  transferido_at: string | null
}

export interface Plan {
  id: string
  nome: string
  valor_mensal: number
  limite_agendamentos: number | null
  features: string[]
  is_active: boolean
}

export interface PlatformSettings {
  default_fee_pct: number
  payout_weekday: number
}
