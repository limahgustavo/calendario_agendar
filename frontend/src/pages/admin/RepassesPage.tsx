import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { payoutsApi } from '@/api/payouts'
import { Button, Card, Badge, Spinner, ErrorMessage } from '@/components/ui'
import {
  formatCurrency,
  formatDateShort,
  PAYOUT_STATUS_LABELS,
  PAYOUT_STATUS_COLORS,
} from '@/lib/utils'
import type { Payout } from '@/types'

function AcoesPayout({ payout }: { payout: Payout }) {
  const queryClient = useQueryClient()

  const approve = useMutation({
    mutationFn: () => payoutsApi.approve(payout.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payouts'] })
    },
  })

  const block = useMutation({
    mutationFn: () => payoutsApi.block(payout.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payouts'] })
    },
  })

  if (payout.status !== 'pendente_aprovacao') return null

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        <Button
          variant="primary"
          disabled={approve.isPending || block.isPending}
          onClick={() => approve.mutate()}
        >
          Aprovar e transferir
        </Button>
        <Button
          variant="danger"
          disabled={approve.isPending || block.isPending}
          onClick={() => block.mutate()}
        >
          Bloquear
        </Button>
      </div>
      {approve.isError && <ErrorMessage error={approve.error} />}
      {block.isError && <ErrorMessage error={block.error} />}
    </div>
  )
}

export default function RepassesPage() {
  const queryClient = useQueryClient()

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['payouts'],
    queryFn: () => payoutsApi.list(),
  })

  const generate = useMutation({
    mutationFn: () => payoutsApi.generate(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payouts'] })
    },
  })

  const exportCsv = useMutation({
    mutationFn: () => payoutsApi.exportCsv(),
  })

  const payouts = data ?? []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Repasses</h1>

      <div className="flex flex-wrap items-center gap-3">
        <Button
          variant="primary"
          disabled={generate.isPending}
          onClick={() => generate.mutate()}
        >
          Gerar repasses da semana
        </Button>
        <Button
          variant="secondary"
          disabled={exportCsv.isPending}
          onClick={() => exportCsv.mutate()}
        >
          Exportar CSV
        </Button>
      </div>

      {generate.isSuccess && (
        <p className="rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-700">
          {generate.data.criados} repasse(s) criado(s).
        </p>
      )}
      {generate.isError && <ErrorMessage error={generate.error} />}
      {exportCsv.isError && <ErrorMessage error={exportCsv.error} />}

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && payouts.length === 0 && (
        <p className="text-gray-500">Nenhum repasse encontrado.</p>
      )}

      {!isLoading && !isError && payouts.length > 0 && (
        <>
          {/* Tabela (desktop) */}
          <Card className="hidden overflow-x-auto p-0 md:block">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-100 bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Studio</th>
                  <th className="px-4 py-3 font-medium">Semana</th>
                  <th className="px-4 py-3 font-medium">Bruto</th>
                  <th className="px-4 py-3 font-medium">Taxa</th>
                  <th className="px-4 py-3 font-medium">Líquido</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Ações</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {payouts.map((p) => (
                  <tr key={p.id}>
                    <td className="px-4 py-3 font-medium text-gray-800">
                      {p.studio_name ?? '—'}
                    </td>
                    <td className="px-4 py-3 text-gray-600">{formatDateShort(p.semana_inicio)}</td>
                    <td className="px-4 py-3 text-gray-600">{formatCurrency(p.valor_bruto)}</td>
                    <td className="px-4 py-3 text-gray-600">
                      {p.taxa_admin_pct}% ({formatCurrency(p.taxa_admin_valor)})
                    </td>
                    <td className="px-4 py-3 font-bold text-gray-800">
                      {formatCurrency(p.valor_liquido)}
                    </td>
                    <td className="px-4 py-3">
                      <Badge className={PAYOUT_STATUS_COLORS[p.status]}>
                        {PAYOUT_STATUS_LABELS[p.status]}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <AcoesPayout payout={p} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Cards (mobile) */}
          <div className="space-y-3 md:hidden">
            {payouts.map((p) => (
              <Card key={p.id} className="space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-gray-800">{p.studio_name ?? '—'}</p>
                    <p className="text-sm text-gray-500">
                      Semana de {formatDateShort(p.semana_inicio)}
                    </p>
                  </div>
                  <Badge className={PAYOUT_STATUS_COLORS[p.status]}>
                    {PAYOUT_STATUS_LABELS[p.status]}
                  </Badge>
                </div>
                <p className="text-sm text-gray-500">Bruto: {formatCurrency(p.valor_bruto)}</p>
                <p className="text-sm text-gray-500">
                  Taxa: {p.taxa_admin_pct}% ({formatCurrency(p.taxa_admin_valor)})
                </p>
                <p className="text-sm text-gray-700">
                  Líquido: <span className="font-bold">{formatCurrency(p.valor_liquido)}</span>
                </p>
                <AcoesPayout payout={p} />
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
