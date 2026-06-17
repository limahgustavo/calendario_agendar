import api from './client'
import type { Payout, PayoutStatus } from '@/types'

export const payoutsApi = {
  list: (status?: PayoutStatus) =>
    api.get<Payout[]>('/payouts', { params: status ? { status } : {} }).then((r) => r.data),
  generate: () => api.post<{ criados: number }>('/payouts/gerar').then((r) => r.data),
  approve: (id: string) => api.post<Payout>(`/payouts/${id}/aprovar`).then((r) => r.data),
  block: (id: string) => api.post<Payout>(`/payouts/${id}/bloquear`).then((r) => r.data),
  exportCsv: async () => {
    const res = await api.get('/payouts/export', { responseType: 'blob' })
    const url = URL.createObjectURL(res.data as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'repasses.csv'
    a.click()
    URL.revokeObjectURL(url)
  },
}
