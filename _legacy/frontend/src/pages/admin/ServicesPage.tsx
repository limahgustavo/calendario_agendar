import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { servicesApi } from '@/api/services'
import type { Service } from '@/types'
import { formatCurrency, cn } from '@/lib/utils'
import { Plus, Pencil, Trash2, X, Check } from 'lucide-react'

const schema = z.object({
  name: z.string().min(2),
  description: z.string().optional(),
  price: z.coerce.number().positive(),
  duration_minutes: z.coerce.number().int().positive(),
})
type FormData = z.infer<typeof schema>

export default function ServicesPage() {
  const qc = useQueryClient()
  const [editing, setEditing] = useState<Service | null>(null)
  const [showForm, setShowForm] = useState(false)

  const { data: services = [] } = useQuery({
    queryKey: ['services-all'],
    queryFn: servicesApi.listAll,
  })

  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { duration_minutes: 60 },
  })

  const create = useMutation({
    mutationFn: (d: FormData) => servicesApi.create(d as Omit<Service, 'id' | 'is_active'>),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['services-all'] }); qc.invalidateQueries({ queryKey: ['services'] }); setShowForm(false); reset() },
  })

  const update = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Service> }) => servicesApi.update(id, data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['services-all'] }); qc.invalidateQueries({ queryKey: ['services'] }); setEditing(null) },
  })

  const remove = useMutation({
    mutationFn: (id: number) => servicesApi.update(id, { is_active: false }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['services-all'] }); qc.invalidateQueries({ queryKey: ['services'] }) },
  })

  function startEdit(svc: Service) {
    setEditing(svc)
    setValue('name', svc.name)
    setValue('description', svc.description ?? '')
    setValue('price', svc.price)
    setValue('duration_minutes', svc.duration_minutes)
    setShowForm(true)
  }

  function onSubmit(data: FormData) {
    if (editing) update.mutate({ id: editing.id, data })
    else create.mutate(data)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">Serviços</h1>
        <button
          onClick={() => { setEditing(null); reset(); setShowForm(!showForm) }}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-xl hover:bg-brand-700 text-sm font-medium"
        >
          <Plus size={16} /> Novo serviço
        </button>
      </div>

      {/* Form */}
      {showForm && (
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
          <h2 className="font-semibold text-gray-700 mb-4">{editing ? 'Editar serviço' : 'Novo serviço'}</h2>
          <form onSubmit={handleSubmit(onSubmit)} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-gray-700">Nome</label>
              <input {...register('name')} className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-400 focus:outline-none" />
              {errors.name && <p className="text-red-500 text-xs mt-0.5">{errors.name.message}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Preço (R$)</label>
              <input type="number" step="0.01" {...register('price')} className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-400 focus:outline-none" />
              {errors.price && <p className="text-red-500 text-xs mt-0.5">{errors.price.message}</p>}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Duração (minutos)</label>
              <input type="number" {...register('duration_minutes')} className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-400 focus:outline-none" />
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Descrição (opcional)</label>
              <input {...register('description')} className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-400 focus:outline-none" />
            </div>
            <div className="sm:col-span-2 flex gap-2">
              <button type="submit" className="flex items-center gap-2 px-4 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 text-sm">
                <Check size={16} /> Salvar
              </button>
              <button type="button" onClick={() => setShowForm(false)} className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm">
                <X size={16} /> Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* List */}
      <div className="grid gap-4 sm:grid-cols-2">
        {services.map((svc) => (
          <div key={svc.id} className={cn('bg-white rounded-2xl border p-5 shadow-sm', !svc.is_active && 'opacity-50')}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-800">{svc.name}</h3>
                {svc.description && <p className="text-sm text-gray-500 mt-0.5">{svc.description}</p>}
                <div className="flex gap-3 mt-2 text-sm">
                  <span className="font-bold text-brand-600">{formatCurrency(svc.price)}</span>
                  <span className="text-gray-400">{svc.duration_minutes} min</span>
                  <span className={cn('px-2 py-0.5 rounded-full text-xs', svc.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500')}>
                    {svc.is_active ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
              </div>
              <div className="flex gap-1">
                <button onClick={() => startEdit(svc)} className="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
                  <Pencil size={15} />
                </button>
                {svc.is_active && (
                  <button onClick={() => remove.mutate(svc.id)} className="p-2 rounded-lg hover:bg-red-50 text-red-400">
                    <Trash2 size={15} />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
