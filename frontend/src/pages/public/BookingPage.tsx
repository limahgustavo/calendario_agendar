import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { format, addMonths, subMonths, isBefore, startOfToday, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { studiosApi } from '@/api/studios'
import { servicesApi } from '@/api/services'
import { availabilityApi } from '@/api/availability'
import { Button, Spinner } from '@/components/ui'
import { cn, formatCurrency, CATEGORY_LABELS, WEEKDAY_SHORT } from '@/lib/utils'
import type { Service, CalendarSlot } from '@/types'

export default function BookingPage() {
  const { slug = '' } = useParams()
  const navigate = useNavigate()
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [service, setService] = useState<Service | null>(null)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [selectedTime, setSelectedTime] = useState<string | null>(null)

  const month = format(currentMonth, 'yyyy-MM')

  const { data: studio, isLoading: loadingStudio, isError } = useQuery({
    queryKey: ['studio', slug],
    queryFn: () => studiosApi.public(slug),
  })
  const { data: services = [] } = useQuery({
    queryKey: ['services', slug],
    queryFn: () => servicesApi.publicList(slug),
    enabled: !!studio,
  })
  const { data: slots = [] } = useQuery({
    queryKey: ['calendar', slug, month],
    queryFn: () => availabilityApi.publicCalendar(slug, month),
    enabled: !!studio,
  })

  if (loadingStudio) return <Spinner />
  if (isError || !studio)
    return <div className="min-h-screen flex items-center justify-center text-gray-500">Studio não encontrado.</div>

  const slotsByDate = slots.reduce<Record<string, CalendarSlot[]>>((acc, s) => {
    ;(acc[s.date] ||= []).push(s)
    return acc
  }, {})

  const today = startOfToday()
  const firstDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1)
  const lastDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0)
  const startPad = (firstDay.getDay() + 6) % 7
  const days: Array<Date | null> = [
    ...Array(startPad).fill(null),
    ...Array.from({ length: lastDay.getDate() }, (_, i) =>
      new Date(currentMonth.getFullYear(), currentMonth.getMonth(), i + 1),
    ),
  ]

  const availableTimes = selectedDate
    ? (slotsByDate[selectedDate] ?? []).filter((s) => s.available)
    : []

  function proceed() {
    if (!service || !selectedDate || !selectedTime) return
    navigate(`/booking/${slug}/dados`, {
      state: { service, date: selectedDate, time_str: selectedTime, studio },
    })
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white py-8 px-4">
      <div className="max-w-2xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-brand-700">{studio.name}</h1>
          <p className="text-gray-500 mt-1">Escolha o serviço, a data e o horário</p>
        </div>

        <section>
          <h2 className="font-semibold text-gray-700 mb-3">1. Serviço</h2>
          {services.length === 0 ? (
            <p className="text-gray-400 text-sm">Nenhum serviço disponível ainda.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {services.map((svc) => (
                <button
                  key={svc.id}
                  onClick={() => setService(svc)}
                  className={cn(
                    'p-4 rounded-xl border-2 text-left transition-all',
                    service?.id === svc.id
                      ? 'border-brand-500 bg-brand-50'
                      : 'border-gray-200 bg-white hover:border-brand-300',
                  )}
                >
                  <div className="text-xs text-brand-500 font-medium">
                    {CATEGORY_LABELS[svc.categoria]}
                  </div>
                  <div className="font-semibold text-gray-800">{svc.name}</div>
                  <div className="text-sm text-gray-500">{svc.duration_minutes} min</div>
                  <div className="text-brand-600 font-bold mt-1">{formatCurrency(svc.price)}</div>
                </button>
              ))}
            </div>
          )}
        </section>

        <section>
          <h2 className="font-semibold text-gray-700 mb-3">2. Data</h2>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
            <div className="flex items-center justify-between mb-4">
              <button onClick={() => setCurrentMonth(subMonths(currentMonth, 1))} className="p-1.5 rounded-lg hover:bg-gray-100">
                <ChevronLeft size={18} />
              </button>
              <span className="font-semibold capitalize">
                {format(currentMonth, 'MMMM yyyy', { locale: ptBR })}
              </span>
              <button onClick={() => setCurrentMonth(addMonths(currentMonth, 1))} className="p-1.5 rounded-lg hover:bg-gray-100">
                <ChevronRight size={18} />
              </button>
            </div>
            <div className="grid grid-cols-7 mb-2">
              {WEEKDAY_SHORT.map((d) => (
                <div key={d} className="text-center text-xs text-gray-400 font-medium py-1">{d}</div>
              ))}
            </div>
            <div className="grid grid-cols-7 gap-1">
              {days.map((day, i) => {
                if (!day) return <div key={i} />
                const iso = format(day, 'yyyy-MM-dd')
                const daySlots = slotsByDate[iso] ?? []
                const hasAvailable = daySlots.some((s) => s.available)
                const isPast = isBefore(day, today)
                const isSelected = selectedDate === iso
                const disabled = isPast || daySlots.length === 0
                return (
                  <button
                    key={iso}
                    disabled={disabled}
                    onClick={() => {
                      setSelectedDate(iso)
                      setSelectedTime(null)
                    }}
                    className={cn(
                      'aspect-square flex items-center justify-center rounded-xl text-sm font-medium transition-all',
                      disabled
                        ? 'text-gray-300 cursor-not-allowed'
                        : isSelected
                          ? 'bg-brand-500 text-white shadow'
                          : hasAvailable
                            ? 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
                            : 'bg-red-50 text-red-400 border border-red-200 cursor-not-allowed',
                    )}
                  >
                    {day.getDate()}
                  </button>
                )
              })}
            </div>
            <div className="flex gap-4 mt-4 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-green-100 border border-green-200 rounded" /> Disponível
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-red-100 border border-red-200 rounded" /> Indisponível
              </span>
            </div>
          </div>
        </section>

        {selectedDate && (
          <section>
            <h2 className="font-semibold text-gray-700 mb-3">
              3. Horário · {format(parseISO(selectedDate), "dd 'de' MMMM", { locale: ptBR })}
            </h2>
            {availableTimes.length === 0 ? (
              <p className="text-gray-400 text-sm">Nenhum horário disponível neste dia.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {availableTimes.map((slot) => (
                  <button
                    key={slot.time_str}
                    onClick={() => setSelectedTime(slot.time_str)}
                    className={cn(
                      'px-4 py-2 rounded-lg border-2 font-medium text-sm transition-all',
                      selectedTime === slot.time_str
                        ? 'border-brand-500 bg-brand-500 text-white'
                        : 'border-gray-200 bg-white hover:border-brand-300 text-gray-700',
                    )}
                  >
                    {slot.time_str}
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        <Button
          onClick={proceed}
          disabled={!service || !selectedDate || !selectedTime}
          className="w-full py-4 text-lg disabled:opacity-40"
        >
          Continuar →
        </Button>
      </div>
    </div>
  )
}
