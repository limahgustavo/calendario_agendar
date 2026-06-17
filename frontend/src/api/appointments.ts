import api from './client'
import type { Appointment, BookingResponse, AppointmentStatus } from '@/types'

export interface BookingPayload {
  service_id: string
  data: string // YYYY-MM-DD
  hora: string // HH:MM
  client_name: string
  client_email: string
  client_phone: string
  client_cpf_cnpj?: string
  notas?: string
}

export const appointmentsApi = {
  book: (slug: string, data: BookingPayload) =>
    api.post<BookingResponse>(`/appointments/${slug}`, data).then((r) => r.data),

  createManual: (data: BookingPayload & { cobrar: boolean }) =>
    api.post<BookingResponse>('/appointments/manual', data).then((r) => r.data),

  studioList: (params?: { status?: AppointmentStatus; pendentes?: boolean }) =>
    api.get<Appointment[]>('/appointments/studio', { params }).then((r) => r.data),

  clientList: () => api.get<Appointment[]>('/appointments/client').then((r) => r.data),

  update: (id: string, data: { status?: AppointmentStatus; notas?: string }) =>
    api.put<Appointment>(`/appointments/${id}`, data).then((r) => r.data),

  confirmByToken: (token: string) =>
    api.post(`/appointments/${token}/confirmar`).then((r) => r.data),

  cancelByToken: (token: string) =>
    api.post(`/appointments/${token}/cancelar`).then((r) => r.data),

  rescheduleByToken: (token: string) =>
    api.post(`/appointments/${token}/remarcar`).then((r) => r.data),

  ratingInfo: (token: string) =>
    api
      .get<{ servico_nome: string; studio_name: string | null; data: string; hora: string; rating: number | null }>(
        `/appointments/${token}/info`,
      )
      .then((r) => r.data),

  submitRating: (token: string, rating: number, comment?: string) =>
    api.post(`/appointments/${token}/avaliar`, { rating, comment }).then((r) => r.data),

  comprovante: async (appointmentId: string) => {
    const res = await api.get(`/payments/${appointmentId}/comprovante`, { responseType: 'blob' })
    const url = URL.createObjectURL(res.data as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `comprovante-${appointmentId}.pdf`
    a.click()
    URL.revokeObjectURL(url)
  },
}
