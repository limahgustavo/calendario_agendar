import { useState, type FormEvent } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { servicesApi } from '@/api/services'
import { Button, Input, Select, Field, Card, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency, CATEGORY_LABELS } from '@/lib/utils'
import type { ServiceCategory } from '@/types'

const EMPTY_FORM = {
  name: '',
  categoria: 'aplicacao' as ServiceCategory,
  price: '',
  duration_minutes: '',
  description: '',
}

export default function ServicosPage() {
  const queryClient = useQueryClient()
  const [form, setForm] = useState(EMPTY_FORM)

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['services'],
    queryFn: servicesApi.list,
  })

  const createMutation = useMutation({
    mutationFn: () =>
      servicesApi.create({
        name: form.name,
        categoria: form.categoria,
        price: Number(form.price),
        duration_minutes: Number(form.duration_minutes),
        description: form.description || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] })
      setForm(EMPTY_FORM)
    },
  })

  const removeMutation = useMutation({
    mutationFn: (id: string) => servicesApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['services'] })
    },
  })

  const services = (data ?? []).filter((s) => s.is_active)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Serviços e preços</h1>

      <Card>
        <h2 className="mb-4 text-lg font-semibold text-gray-700">Adicionar serviço</h2>
        <form
          onSubmit={(e: FormEvent) => {
            e.preventDefault()
            createMutation.mutate()
          }}
          className="space-y-4"
        >
          <Field label="Nome">
            <Input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </Field>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Field label="Categoria">
              <Select
                value={form.categoria}
                onChange={(e) => setForm({ ...form, categoria: e.target.value as ServiceCategory })}
              >
                {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Preço (R$)">
              <Input
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
                required
              />
            </Field>
            <Field label="Duração (min)">
              <Input
                type="number"
                min="0"
                step="1"
                value={form.duration_minutes}
                onChange={(e) => setForm({ ...form, duration_minutes: e.target.value })}
                required
              />
            </Field>
          </div>

          <Field label="Descrição (opcional)">
            <Input
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </Field>

          {createMutation.isError && <ErrorMessage error={createMutation.error} />}

          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Salvando...' : 'Adicionar serviço'}
          </Button>
        </form>
      </Card>

      <section className="space-y-3">
        <h2 className="text-lg font-semibold text-gray-700">Serviços cadastrados</h2>

        {isLoading && <Spinner />}
        {isError && <ErrorMessage error={error} />}

        {!isLoading && !isError && services.length === 0 && (
          <p className="text-gray-500">Nenhum serviço cadastrado.</p>
        )}

        {!isLoading && !isError && services.length > 0 && (
          <div className="space-y-3">
            {services.map((s) => (
              <Card
                key={s.id}
                className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="space-y-1">
                  <p className="text-xs font-medium uppercase tracking-wide text-brand-600">
                    {CATEGORY_LABELS[s.categoria]}
                  </p>
                  <p className="font-bold text-gray-800">{s.name}</p>
                  {s.description && <p className="text-sm text-gray-500">{s.description}</p>}
                  <p className="text-sm text-gray-500">{s.duration_minutes} min</p>
                </div>
                <div className="flex flex-col items-start gap-2 sm:items-end">
                  <p className="font-semibold text-brand-600">{formatCurrency(s.price)}</p>
                  <Button
                    variant="danger"
                    onClick={() => removeMutation.mutate(s.id)}
                    disabled={removeMutation.isPending}
                  >
                    Remover
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {removeMutation.isError && <ErrorMessage error={removeMutation.error} />}
      </section>
    </div>
  )
}
