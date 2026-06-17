import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format, addMonths, subMonths } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { ChevronLeft, ChevronRight, Save } from 'lucide-react'
import { availabilityApi } from '@/api/availability'
import { WEEKDAY_NAMES, cn } from '@/lib/utils'

const DEFAULT_TIMES = ['08:00', '09:00', '10:00', '11:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']

export default function AvailabilityPage() {
  const qc = useQueryClient()
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const monthYear = format(currentMonth, 'yyyy-MM')

  // Selected weekdays (0=Mon..6=Sun) and times
  const [selectedWeekdays, setSelectedWeekdays] = useState<Set<number>>(new Set())
  const [selectedTimes, setSelectedTimes] = useState<Set<string>>(new Set())
  const [customTime, setCustomTime] = useState('')
  const [extraTimes, setExtraTimes] = useState<string[]>([])

  const { data: existing = [] } = useQuery({
    queryKey: ['slots-admin', monthYear],
    queryFn: () => availabilityApi.listSlots(monthYear),
  })

  const save = useMutation({
    mutationFn: () =>
      availabilityApi.bulkCreate({
        month_year: monthYear,
        weekdays: Array.from(selectedWeekdays),
        times: Array.from(selectedTimes),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['slots-admin'] })
      qc.invalidateQueries({ queryKey: ['calendar'] })
      alert('Disponibilidade salva com sucesso!')
    },
  })

  function toggleWeekday(d: number) {
    setSelectedWeekdays((prev) => {
      const next = new Set(prev)
      next.has(d) ? next.delete(d) : next.add(d)
      return next
    })
  }

  function toggleTime(t: string) {
    setSelectedTimes((prev) => {
      const next = new Set(prev)
      next.has(t) ? next.delete(t) : next.add(t)
      return next
    })
  }

  function addCustomTime() {
    if (!customTime) return
    setExtraTimes((p) => [...new Set([...p, customTime])])
    setSelectedTimes((p) => new Set([...p, customTime]))
    setCustomTime('')
  }

  const allTimes = [...DEFAULT_TIMES, ...extraTimes.filter((t) => !DEFAULT_TIMES.includes(t))]

  // Summarize existing config
  const existingByWeekday: Record<number, string[]> = {}
  for (const s of existing as Array<{ weekday: number; time_str: string }>) {
    if (!existingByWeekday[s.weekday]) existingByWeekday[s.weekday] = []
    existingByWeekday[s.weekday].push(s.time_str)
  }

  return (
    <div className="space-y-6">
      {/* Month nav */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Disponibilidade</h1>
        <div className="flex items-center gap-2">
          <button onClick={() => setCurrentMonth(subMonths(currentMonth, 1))} className="p-1.5 rounded-lg hover:bg-gray-100"><ChevronLeft size={18} /></button>
          <span className="font-semibold capitalize min-w-[120px] text-center">
            {format(currentMonth, 'MMMM yyyy', { locale: ptBR })}
          </span>
          <button onClick={() => setCurrentMonth(addMonths(currentMonth, 1))} className="p-1.5 rounded-lg hover:bg-gray-100"><ChevronRight size={18} /></button>
        </div>
      </div>

      {/* Existing config summary */}
      {existing.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-2xl p-4">
          <p className="text-sm font-medium text-green-700 mb-2">Configuração atual para {monthYear}:</p>
          <div className="space-y-1">
            {Object.entries(existingByWeekday).map(([wd, times]) => (
              <div key={wd} className="text-sm text-green-600">
                <strong>{WEEKDAY_NAMES[Number(wd)]}</strong>: {times.sort().join(', ')}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-6">
        <p className="text-sm text-gray-500">Configure os dias da semana e horários disponíveis para o mês selecionado. Isso substituirá a configuração atual.</p>

        {/* Weekdays */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3">Dias da semana</label>
          <div className="flex flex-wrap gap-2">
            {WEEKDAY_NAMES.map((name, i) => (
              <button
                key={i}
                onClick={() => toggleWeekday(i)}
                className={cn(
                  'px-4 py-2 rounded-xl border-2 text-sm font-medium transition-all',
                  selectedWeekdays.has(i)
                    ? 'border-brand-500 bg-brand-50 text-brand-700'
                    : 'border-gray-200 text-gray-600 hover:border-brand-300',
                )}
              >
                {name}
              </button>
            ))}
          </div>
        </div>

        {/* Times */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-3">Horários</label>
          <div className="flex flex-wrap gap-2">
            {allTimes.map((t) => (
              <button
                key={t}
                onClick={() => toggleTime(t)}
                className={cn(
                  'px-4 py-2 rounded-xl border-2 text-sm font-medium transition-all',
                  selectedTimes.has(t)
                    ? 'border-brand-500 bg-brand-50 text-brand-700'
                    : 'border-gray-200 text-gray-600 hover:border-brand-300',
                )}
              >
                {t}
              </button>
            ))}
          </div>
          <div className="flex gap-2 mt-3">
            <input
              type="time"
              value={customTime}
              onChange={(e) => setCustomTime(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-brand-400 focus:outline-none"
            />
            <button onClick={addCustomTime} className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200">
              + Adicionar horário
            </button>
          </div>
        </div>

        {/* Save */}
        <button
          onClick={() => save.mutate()}
          disabled={selectedWeekdays.size === 0 || selectedTimes.size === 0 || save.isPending}
          className="flex items-center gap-2 px-6 py-3 bg-brand-600 text-white font-semibold rounded-xl hover:bg-brand-700 disabled:opacity-40 transition-colors"
        >
          <Save size={16} />
          {save.isPending ? 'Salvando...' : 'Salvar disponibilidade'}
        </button>
      </div>
    </div>
  )
}
