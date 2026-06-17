import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import { Button, Input, Select, Field, Card, Spinner, ErrorMessage } from '@/components/ui'
import { WEEKDAY_NAMES } from '@/lib/utils'

export default function ConfiguracoesPage() {
  const queryClient = useQueryClient()

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['settings'],
    queryFn: adminApi.getSettings,
  })

  const [feePct, setFeePct] = useState('')
  const [weekday, setWeekday] = useState('0')

  useEffect(() => {
    if (data) {
      setFeePct(String(data.default_fee_pct))
      setWeekday(String(data.payout_weekday))
    }
  }, [data])

  const mutation = useMutation({
    mutationFn: () =>
      adminApi.updateSettings({
        default_fee_pct: Number(feePct),
        payout_weekday: Number(weekday),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Configurações</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && data && (
        <Card className="max-w-md">
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault()
              mutation.mutate()
            }}
          >
            <Field label="Taxa da plataforma (%)">
              <Input
                type="number"
                min={0}
                step="0.1"
                value={feePct}
                onChange={(e) => setFeePct(e.target.value)}
              />
            </Field>

            <Field label="Dia do repasse">
              <Select value={weekday} onChange={(e) => setWeekday(e.target.value)}>
                {WEEKDAY_NAMES.map((name, index) => (
                  <option key={index} value={index}>
                    {name}
                  </option>
                ))}
              </Select>
            </Field>

            {mutation.isError && <ErrorMessage error={mutation.error} />}
            {mutation.isSuccess && (
              <p className="rounded-xl border border-green-200 bg-green-50 p-3 text-sm text-green-700">
                Configurações salvas com sucesso.
              </p>
            )}

            <Button type="submit" variant="primary" disabled={mutation.isPending}>
              Salvar
            </Button>
          </form>
        </Card>
      )}
    </div>
  )
}
