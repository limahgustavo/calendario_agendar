import api from './client'
import type { Studio, StudioPublic, PaymentMode } from '@/types'

export const studiosApi = {
  register: (data: {
    designer_name: string
    email: string
    whatsapp?: string
    studio_name: string
  }) => api.post<{ message: string; slug: string }>('/studios/register', data).then((r) => r.data),

  me: () => api.get<Studio>('/studios/me').then((r) => r.data),

  update: (
    data: Partial<{
      name: string
      email: string
      whatsapp: string
      payment_mode: PaymentMode
      pix_key: string
      bank_info: string
    }>,
  ) => api.put<Studio>('/studios/me', data).then((r) => r.data),

  public: (slug: string) =>
    api.get<StudioPublic>(`/studios/${slug}/public`).then((r) => r.data),
}
