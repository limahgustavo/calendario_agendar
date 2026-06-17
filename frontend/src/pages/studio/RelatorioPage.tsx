import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Star } from 'lucide-react'
import { dashboardApi } from '@/api/dashboard'
import { Card, Select, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency } from '@/lib/utils'

const MESES = [
  'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez',
]

export default function RelatorioPage() {
  const currentYear = new Date().getFullYear()
  const [ano, setAno] = useState(currentYear)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['studio-report', ano],
    queryFn: () => dashboardApi.relatorio(ano),
  })

  const totalRecebido = data?.meses.reduce((s, m) => s + m.recebido, 0) ?? 0
  const totalAg = data?.meses.reduce((s, m) => s + m.total, 0) ?? 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Relatórios</h1>
        <Select value={ano} onChange={(e) => setAno(Number(e.target.value))} className="w-32">
          {[currentYear, currentYear - 1, currentYear - 2].map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </Select>
      </div>

      {isLoading ? (
        <Spinner />
      ) : isError ? (
        <ErrorMessage error={error} />
      ) : data ? (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <Card>
              <div className="text-sm text-gray-500">Recebido no ano</div>
              <div className="text-2xl font-bold text-brand-700">{formatCurrency(totalRecebido)}</div>
            </Card>
            <Card>
              <div className="text-sm text-gray-500">Agendamentos</div>
              <div className="text-2xl font-bold text-gray-800">{totalAg}</div>
            </Card>
            <Card>
              <div className="text-sm text-gray-500">Avaliação média</div>
              <div className="text-2xl font-bold text-gray-800 flex items-center gap-1">
                {data.media_avaliacao ?? '—'}
                {data.media_avaliacao != null && (
                  <Star size={18} className="fill-yellow-400 text-yellow-400" />
                )}
                <span className="text-sm font-normal text-gray-400">
                  ({data.total_avaliacoes})
                </span>
              </div>
            </Card>
          </div>

          <Card className="overflow-x-auto">
            <h2 className="font-semibold text-gray-700 mb-3">Por mês</h2>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-400 border-b">
                  <th className="py-2">Mês</th>
                  <th className="py-2 text-right">Recebido</th>
                  <th className="py-2 text-right">Agend.</th>
                  <th className="py-2 text-right">Realizados</th>
                  <th className="py-2 text-right">Cancelados</th>
                </tr>
              </thead>
              <tbody>
                {data.meses.map((m) => (
                  <tr key={m.mes} className="border-b last:border-0">
                    <td className="py-2 font-medium">{MESES[m.mes - 1]}</td>
                    <td className="py-2 text-right">{formatCurrency(m.recebido)}</td>
                    <td className="py-2 text-right">{m.total}</td>
                    <td className="py-2 text-right text-green-600">{m.realizados}</td>
                    <td className="py-2 text-right text-red-500">{m.cancelados}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <Card>
            <h2 className="font-semibold text-gray-700 mb-3">Serviços mais agendados</h2>
            {data.servicos_top.length === 0 ? (
              <p className="text-gray-400 text-sm">Sem dados no período.</p>
            ) : (
              <ul className="space-y-2">
                {data.servicos_top.map((s) => (
                  <li key={s.nome} className="flex justify-between text-sm">
                    <span className="text-gray-700">{s.nome}</span>
                    <span className="font-semibold">{s.qtd}</span>
                  </li>
                ))}
              </ul>
            )}
          </Card>
        </>
      ) : null}
    </div>
  )
}
