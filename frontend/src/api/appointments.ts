import api from './client'
import type { Appointment, AppointmentStatus } from '@/types'

export interface CreateAppointmentPayload {
  service_id: number
  scheduled_at: string
  client_name: string
  client_email: string
  client_phone: string
  client_cpf_cnpj?: string
  notes?: string
}

export interface BookingResponse {
  appointment_id: number
  payment_link: string
  message: string
}

export const appointmentsApi = {
  create: (data: CreateAppointmentPayload) =>
    api.post<BookingResponse>('/appointments', data).then((r) => r.data),

  list: (params?: { status?: AppointmentStatus; month_year?: string }) =>
    api.get<Appointment[]>('/appointments', { params }).then((r) => r.data),

  update: (id: number, data: { status?: AppointmentStatus; notes?: string }) =>
    api.put<Appointment>(`/appointments/${id}`, data).then((r) => r.data),

  confirmByToken: (token: string) =>
    api.post(`/appointments/${token}/confirmar`).then((r) => r.data),

  cancelByToken: (token: string) =>
    api.post(`/appointments/${token}/cancelar`).then((r) => r.data),

  rescheduleByToken: (token: string) =>
    api.post(`/appointments/${token}/remarcar`).then((r) => r.data),
}
