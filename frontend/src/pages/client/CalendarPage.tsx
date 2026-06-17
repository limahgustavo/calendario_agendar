import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { format, addMonths, subMonths, parseISO, isBefore, startOfToday } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { availabilityApi } from '@/api/availability'
import { servicesApi } from '@/api/services'
import type { CalendarSlot, Service } from '@/types'
import { cn } from '@/lib/utils'

export default function CalendarPage() {
  const navigate = useNavigate()
  const [currentMonth, setCurrentMonth] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [selectedTime, setSelectedTime] = useState<string | null>(null)
  const [selectedService, setSelectedService] = useState<Service | null>(null)

  const monthYear = format(currentMonth, 'yyyy-MM')

  const { data: slots = [] } = useQuery<CalendarSlot[]>({
    queryKey: ['calendar', monthYear],
    queryFn: () => availabilityApi.getCalendar(monthYear),
  })

  const { data: services = [] } = useQuery<Service[]>({
    queryKey: ['services'],
    queryFn: servicesApi.list,
  })

  // Group slots by date
  const slotsByDate = slots.reduce<Record<string, CalendarSlot[]>>((acc, slot) => {
    if (!acc[slot.date]) acc[slot.date] = []
    acc[slot.date].push(slot)
    return acc
  }, {})

  const today = startOfToday()

  // Build calendar grid
  const firstDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1)
  const lastDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0)
  const startPad = (firstDay.getDay() + 6) % 7 // Monday=0
  const days: Array<Date | null> = [
    ...Array(startPad).fill(null),
    ...Array.from({ length: lastDay.getDate() }, (_, i) => new Date(currentMonth.getFullYear(), currentMonth.getMonth(), i + 1)),
  ]

  const dateSlots = selectedDate ? (slotsByDate[selectedDate] ?? []) : []
  const availableTimes = dateSlots.filter((s) => s.available)

  function proceed() {
    if (!selectedService || !selectedDate || !selectedTime) return
    sessionStorage.setItem(
      'booking',
      JSON.stringify({ service: selectedService, date: selectedDate, time_str: selectedTime }),
    )
    navigate('/agendar')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white py-10 px-4">
      <div className="max-w-2xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-brand-700">💅 Agende seu horário</h1>
          <p className="text-gray-500 mt-1">Escolha o serviço, data e horário disponível</p>
        </div>

        {/* Services */}
        <section>
          <h2 className="font-semibold text-gray-700 mb-3">1. Escolha o serviço</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {services.map((svc) => (
              <button
                key={svc.id}
                onClick={() => setSelectedService(svc)}
                className={cn(
                  'p-4 rounded-xl border-2 text-left transition-all',
                  selectedService?.id === svc.id
                    ? 'border-brand-500 bg-brand-50'
                    : 'border-gray-200 bg-white hover:border-brand-300',
                )}
              >
                <div className="font-semibold text-gray-800">{svc.name}</div>
                <div className="text-sm text-gray-500 mt-0.5">{svc.duration_minutes} min</div>
                <div className="text-brand-600 font-bold mt-1">
                  R$ {svc.price.toFixed(2).replace('.', ',')}
                </div>
                {svc.description && (
                  <div className="text-xs text-gray-400 mt-1">{svc.description}</div>
                )}
              </button>
            ))}
          </div>
        </section>

        {/* Calendar */}
        <section>
          <h2 className="font-semibold text-gray-700 mb-3">2. Escolha a data</h2>
          <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-4">
            {/* Month nav */}
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}
                className="p-1.5 rounded-lg hover:bg-gray-100"
              >
                <ChevronLeft size={18} />
              </button>
              <span className="font-semibold capitalize">
                {format(currentMonth, 'MMMM yyyy', { locale: ptBR })}
              </span>
              <button
                onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}
                className="p-1.5 rounded-lg hover:bg-gray-100"
              >
                <ChevronRight size={18} />
              </button>
            </div>

            {/* Weekday headers */}
            <div className="grid grid-cols-7 mb-2">
              {['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'].map((d) => (
                <div key={d} className="text-center text-xs text-gray-400 font-medium py-1">{d}</div>
              ))}
            </div>

            {/* Days */}
            <div className="grid grid-cols-7 gap-1">
              {days.map((day, i) => {
                if (!day) return <div key={i} />
                const iso = format(day, 'yyyy-MM-dd')
                const daySlots = slotsByDate[iso] ?? []
                const hasAvailable = daySlots.some((s) => s.available)
                const hasBooked = daySlots.some((s) => !s.available)
                const isPast = isBefore(day, today)
                const isSelected = selectedDate === iso

                return (
                  <button
                    key={iso}
                    disabled={isPast || daySlots.length === 0}
                    onClick={() => { setSelectedDate(iso); setSelectedTime(null) }}
                    className={cn(
                      'aspect-square flex flex-col items-center justify-center rounded-xl text-sm font-medium transition-all',
                      isPast || daySlots.length === 0
                        ? 'text-gray-300 cursor-not-allowed'
                        : isSelected
                        ? 'bg-brand-500 text-white shadow'
                        : hasAvailable
                        ? 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
                        : 'bg-red-50 text-red-400 border border-red-200 cursor-not-allowed',
                    )}
                  >
                    {day.getDate()}
                    {hasAvailable && !isSelected && (
                      <span className="w-1 h-1 bg-green-500 rounded-full mt-0.5" />
                    )}
                  </button>
                )
              })}
            </div>

            <div className="flex gap-4 mt-4 text-xs text-gray-500">
              <span className="flex items-center gap-1"><span className="w-3 h-3 bg-green-100 border border-green-200 rounded" /> Disponível</span>
              <span className="flex items-center gap-1"><span className="w-3 h-3 bg-red-100 border border-red-200 rounded" /> Indisponível</span>
            </div>
          </div>
        </section>

        {/* Time slots */}
        {selectedDate && (
          <section>
            <h2 className="font-semibold text-gray-700 mb-3">3. Escolha o horário</h2>
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

        {/* CTA */}
        <button
          onClick={proceed}
          disabled={!selectedService || !selectedDate || !selectedTime}
          className="w-full py-4 bg-brand-600 text-white font-bold rounded-2xl shadow hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors text-lg"
        >
          Continuar →
        </button>
      </div>
    </div>
  )
}
