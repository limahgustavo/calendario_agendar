import { useState, useEffect, type FormEvent } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { availabilityApi } from '@/api/availability'
import { Button, Input, Card, Spinner, ErrorMessage } from '@/components/ui'
import { WEEKDAY_NAMES, cn } from '@/lib/utils'

function currentMonthValue(): string {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
}

export default function DisponibilidadePage() {
  const [month, setMonth] = useState<string>(currentMonthValue())
  const [ano, mesStr] = month.split('-')
  const anoNum = Number(ano)
  const mesNum = Number(mesStr)

  const [diasSemana, setDiasSemana] = useState<number[]>([])
  const [horarios, setHorarios] = useState<string[]>([])
  const [novoHorario, setNovoHorario] = useState('')
  const [saved, setSaved] = useState(false)

  const configQuery = useQuery({
    queryKey: ['availability', anoNum, mesNum],
    queryFn: () => availabilityApi.getConfig(anoNum, mesNum),
  })

  useEffect(() => {
    setSaved(false)
    setDiasSemana(configQuery.data?.dias_semana ?? [])
    setHorarios(configQuery.data?.horarios ?? [])
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [configQuery.data, month])

  const mutation = useMutation({
    mutationFn: () =>
      availabilityApi.upsertConfig({
        ano: anoNum,
        mes: mesNum,
        dias_semana: diasSemana,
        horarios,
      }),
    onSuccess: () => setSaved(true),
  })

  const toggleDay = (index: number) => {
    setSaved(false)
    setDiasSemana((prev) =>
      prev.includes(index) ? prev.filter((d) => d !== index) : [...prev, index].sort((a, b) => a - b),
    )
  }

  const addHorario = () => {
    const value = novoHorario.trim()
    if (!value || horarios.includes(value)) return
    setSaved(false)
    setHorarios((prev) => [...prev, value].sort())
    setNovoHorario('')
  }

  const removeHorario = (value: string) => {
    setSaved(false)
    setHorarios((prev) => prev.filter((h) => h !== value))
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Disponibilidade</h1>

      <Card className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Mês</label>
        <Input
          type="month"
          value={month}
          onChange={(e) => setMonth(e.target.value)}
          className="sm:w-56"
        />
      </Card>

      {configQuery.isLoading && <Spinner />}
      {configQuery.isError && <ErrorMessage error={configQuery.error} />}

      {!configQuery.isLoading && !configQuery.isError && (
        <form
          onSubmit={(e: FormEvent) => {
            e.preventDefault()
            mutation.mutate()
          }}
          className="space-y-6"
        >
          <Card className="space-y-3">
            <p className="text-sm font-medium text-gray-700">Dias da semana atendidos</p>
            <div className="flex flex-wrap gap-2">
              {WEEKDAY_NAMES.map((name, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => toggleDay(index)}
                  className={cn(
                    'px-4 py-1.5 rounded-full text-sm font-medium transition-colors',
                    diasSemana.includes(index)
                      ? 'bg-brand-600 text-white'
                      : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50',
                  )}
                >
                  {name}
                </button>
              ))}
            </div>
          </Card>

          <Card className="space-y-3">
            <p className="text-sm font-medium text-gray-700">Horários disponíveis</p>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <Input
                type="time"
                value={novoHorario}
                onChange={(e) => setNovoHorario(e.target.value)}
                className="sm:w-56"
              />
              <Button type="button" variant="secondary" onClick={addHorario}>
                Adicionar
              </Button>
            </div>
            {horarios.length === 0 ? (
              <p className="text-sm text-gray-500">Nenhum horário adicionado.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {horarios.map((h) => (
                  <span
                    key={h}
                    className="inline-flex items-center gap-2 rounded-full bg-brand-50 px-3 py-1 text-sm text-brand-700"
                  >
                    {h}
                    <button
                      type="button"
                      onClick={() => removeHorario(h)}
                      className="text-brand-500 hover:text-brand-700"
                      aria-label={`Remover ${h}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </Card>

          {mutation.isError && <ErrorMessage error={mutation.error} />}
          {saved && <p className="text-sm font-medium text-green-700">Disponibilidade salva com sucesso!</p>}

          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Salvando...' : 'Salvar'}
          </Button>
        </form>
      )}
    </div>
  )
}
