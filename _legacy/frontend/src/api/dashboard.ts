import api from './client'
import type { DashboardSummary, RevenueSummary } from '@/types'

export const dashboardApi = {
  summary: () => api.get<DashboardSummary>('/dashboard/summary').then((r) => r.data),
  revenue: (monthYear: string) =>
    api.get<RevenueSummary>('/dashboard/revenue', { params: { month_year: monthYear } }).then((r) => r.data),
}
