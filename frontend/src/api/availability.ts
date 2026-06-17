import api from './client'
import type { CalendarSlot, Availability } from '@/types'

export const availabilityApi = {
  publicCalendar: (slug: string, month: string) =>
    api
      .get<CalendarSlot[]>(`/availability/${slug}/calendar`, { params: { month } })
      .then((r) => r.data),

  getConfig: (ano: number, mes: number) =>
    api.get<Availability | null>('/availability', { params: { ano, mes } }).then((r) => r.data),

  upsertConfig: (data: { ano: number; mes: number; dias_semana: number[]; horarios: string[] }) =>
    api.post<Availability>('/availability', data).then((r) => r.data),
}
