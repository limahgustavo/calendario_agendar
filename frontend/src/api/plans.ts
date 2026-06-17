import api from './client'
import type { Plan } from '@/types'

export const plansApi = {
  list: () => api.get<Plan[]>('/plans').then((r) => r.data),
  subscribe: (plan_id: string) =>
    api.post<Plan>('/plans/studio/subscribe', { plan_id }).then((r) => r.data),
}
