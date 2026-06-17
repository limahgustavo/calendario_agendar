import { useQuery } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import { Card, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency } from '@/lib/utils'

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-800">{value}</p>
    </Card>
  )
}

export default function DashboardPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: adminApi.dashboard,
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Visão geral</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="Faturado no mês" value={formatCurrency(data.faturado_mes)} />
            <StatCard label="Repasses pendentes" value={formatCurrency(data.repasses_pendentes)} />
            <StatCard label="Clientes ativos" value={data.clientes_ativos} />
            <StatCard label="Studios ativos" value={data.studios_ativos} />
          </div>

          <p className="text-sm text-gray-500">
            Taxa da plataforma: <span className="font-semibold text-gray-700">{data.taxa_padrao}%</span>
          </p>
        </>
      )}
    </div>
  )
}
