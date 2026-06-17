import api from './client'
import type { StudioDashboard } from '@/types'

export interface StudioReport {
  ano: number
  meses: { mes: number; recebido: number; total: number; realizados: number; cancelados: number }[]
  media_avaliacao: number | null
  total_avaliacoes: number
  servicos_top: { nome: string; qtd: number }[]
}

export const dashboardApi = {
  studio: () => api.get<StudioDashboard>('/dashboard/studio').then((r) => r.data),
  relatorio: (ano: number) =>
    api.get<StudioReport>('/dashboard/studio/relatorio', { params: { ano } }).then((r) => r.data),
}
