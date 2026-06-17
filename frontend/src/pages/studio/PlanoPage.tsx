import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { plansApi } from '@/api/plans'
import { studiosApi } from '@/api/studios'
import { Button, Card, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency, cn } from '@/lib/utils'
import type { Plan } from '@/types'

function PlanCard({ plan, isCurrent }: { plan: Plan; isCurrent: boolean }) {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: () => plansApi.subscribe(plan.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-studio'] })
    },
  })

  return (
    <Card
      className={cn(
        'flex flex-col gap-4',
        isCurrent ? 'border-brand-500 ring-1 ring-brand-500' : '',
      )}
    >
      <div className="space-y-1">
        <p className="text-lg font-bold text-gray-800">{plan.nome}</p>
        <p className="text-2xl font-bold text-brand-600">
          {formatCurrency(plan.valor_mensal)}
          <span className="text-sm font-medium text-gray-500">/mês</span>
        </p>
        <p className="text-sm text-gray-500">
          {plan.limite_agendamentos
            ? `Até ${plan.limite_agendamentos} agendamentos/mês`
            : 'Ilimitado'}
        </p>
      </div>

      {plan.features.length > 0 && (
        <ul className="space-y-1 text-sm text-gray-600">
          {plan.features.map((f, i) => (
            <li key={i} className="flex items-start gap-2">
              <span className="text-brand-500">✓</span>
              {f}
            </li>
          ))}
        </ul>
      )}

      <div className="mt-auto space-y-2">
        <Button
          className="w-full"
          variant={isCurrent ? 'secondary' : 'primary'}
          disabled={isCurrent || mutation.isPending}
          onClick={() => mutation.mutate()}
        >
          {isCurrent ? 'Plano atual' : mutation.isPending ? 'Aguarde...' : 'Assinar'}
        </Button>
        {mutation.isError && <ErrorMessage error={mutation.error} />}
      </div>
    </Card>
  )
}

export default function PlanoPage() {
  const plansQuery = useQuery({ queryKey: ['plans'], queryFn: plansApi.list })
  const studioQuery = useQuery({ queryKey: ['my-studio'], queryFn: studiosApi.me })

  const isLoading = plansQuery.isLoading || studioQuery.isLoading
  const isError = plansQuery.isError || studioQuery.isError
  const error = plansQuery.error || studioQuery.error

  const plano = studioQuery.data?.plano
  const isCurrentPlan = (plan: Plan) =>
    plano === plan.id || plano?.toLowerCase() === plan.nome.toLowerCase()

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Plano</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && plansQuery.data && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {plansQuery.data.map((plan) => (
            <PlanCard key={plan.id} plan={plan} isCurrent={isCurrentPlan(plan)} />
          ))}
        </div>
      )}
    </div>
  )
}
