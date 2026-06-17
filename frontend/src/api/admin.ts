import api from './client'
import type { AdminDashboard, ClientRow, StudioRow, PlatformSettings } from '@/types'

export const adminApi = {
  dashboard: () => api.get<AdminDashboard>('/admin/dashboard').then((r) => r.data),
  clients: () => api.get<ClientRow[]>('/admin/clients').then((r) => r.data),
  blockClient: (id: string) =>
    api.post<{ is_active: boolean }>(`/admin/clients/${id}/block`).then((r) => r.data),
  studios: () => api.get<StudioRow[]>('/admin/studios').then((r) => r.data),
  blockStudio: (id: string) =>
    api.post<{ is_active: boolean }>(`/admin/studios/${id}/block`).then((r) => r.data),
  verifyBank: (id: string) =>
    api.post<{ bank_verified: boolean }>(`/admin/studios/${id}/verificar-banco`).then((r) => r.data),
  getSettings: () => api.get<PlatformSettings>('/admin/settings').then((r) => r.data),
  updateSettings: (data: Partial<PlatformSettings>) =>
    api.put<PlatformSettings>('/admin/settings', data).then((r) => r.data),
}
