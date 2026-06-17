import api from './client'
import type { Service } from '@/types'

export const servicesApi = {
  list: () => api.get<Service[]>('/services').then((r) => r.data),
  listAll: () => api.get<Service[]>('/services/all').then((r) => r.data),
  create: (data: Omit<Service, 'id' | 'is_active'>) =>
    api.post<Service>('/services', data).then((r) => r.data),
  update: (id: number, data: Partial<Service>) =>
    api.put<Service>(`/services/${id}`, data).then((r) => r.data),
  remove: (id: number) => api.delete(`/services/${id}`),
}
