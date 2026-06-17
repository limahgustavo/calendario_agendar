import api from './client'
import type { CalendarSlot } from '@/types'

export const availabilityApi = {
  getCalendar: (monthYear: string) =>
    api.get<CalendarSlot[]>('/availability/calendar', { params: { month_year: monthYear } }).then((r) => r.data),

  listSlots: (monthYear: string) =>
    api.get('/availability', { params: { month_year: monthYear } }).then((r) => r.data),

  bulkCreate: (data: { month_year: string; weekdays: number[]; times: string[] }) =>
    api.post('/availability/bulk', data).then((r) => r.data),

  deleteSlot: (id: number) => api.delete(`/availability/${id}`),
}
