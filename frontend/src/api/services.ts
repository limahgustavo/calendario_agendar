import api from './client'
import type { Service, ServiceCategory } from '@/types'

export interface ServicePayload {
  name: string
  categoria: ServiceCategory
  description?: string
  price: number
  duration_minutes: number
}

export const servicesApi = {
  publicList: (slug: string) =>
    api.get<Service[]>(`/services/public/${slug}`).then((r) => r.data),

  list: () => api.get<Service[]>('/services').then((r) => r.data),

  create: (data: ServicePayload) => api.post<Service>('/services', data).then((r) => r.data),

  update: (id: string, data: Partial<ServicePayload & { is_active: boolean }>) =>
    api.put<Service>(`/services/${id}`, data).then((r) => r.data),

  remove: (id: string) => api.delete(`/services/${id}`).then((r) => r.data),
}
