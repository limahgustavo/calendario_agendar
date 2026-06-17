import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value)
}

export function formatDate(isoDate: string): string {
  return format(parseISO(isoDate), "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
}

export function formatDateShort(isoDate: string): string {
  return format(parseISO(isoDate), 'dd/MM/yyyy', { locale: ptBR })
}

export function formatDateTime(isoDate: string): string {
  return format(parseISO(isoDate), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })
}

export const WEEKDAY_NAMES = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
export const WEEKDAY_SHORT = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']

export const STATUS_LABELS: Record<string, string> = {
  agendado: 'Aguardando pagamento',
  confirmado: 'Confirmado',
  cancelado: 'Cancelado',
  realizado: 'Realizado',
  remarcado: 'Remarcado',
}

export const STATUS_COLORS: Record<string, string> = {
  agendado: 'bg-yellow-100 text-yellow-800',
  confirmado: 'bg-green-100 text-green-800',
  cancelado: 'bg-red-100 text-red-800',
  realizado: 'bg-blue-100 text-blue-800',
  remarcado: 'bg-purple-100 text-purple-800',
}

export const CATEGORY_LABELS: Record<string, string> = {
  aplicacao: 'Aplicação',
  manutencao: 'Manutenção',
  outros: 'Outros',
}

export const PAYOUT_STATUS_LABELS: Record<string, string> = {
  pendente_aprovacao: 'Pendente',
  aprovado: 'Aprovado',
  transferido: 'Transferido',
  bloqueado: 'Bloqueado',
}

export const PAYOUT_STATUS_COLORS: Record<string, string> = {
  pendente_aprovacao: 'bg-yellow-100 text-yellow-800',
  aprovado: 'bg-blue-100 text-blue-800',
  transferido: 'bg-green-100 text-green-800',
  bloqueado: 'bg-red-100 text-red-800',
}
