import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import { Button, Card, Badge, Spinner, ErrorMessage } from '@/components/ui'
import type { StudioRow } from '@/types'

function StatusBadge({ active }: { active: boolean }) {
  return (
    <Badge className={active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
      {active ? 'Ativo' : 'Bloqueado'}
    </Badge>
  )
}

function AcaoButton({ studio }: { studio: StudioRow }) {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: () => adminApi.blockStudio(studio.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-studios'] })
    },
  })

  return (
    <Button
      variant={studio.is_active ? 'secondary' : 'primary'}
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      {studio.is_active ? 'Bloquear' : 'Reativar'}
    </Button>
  )
}

function BancoCell({ studio }: { studio: StudioRow }) {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: () => adminApi.verifyBank(studio.id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-studios'] }),
  })
  return (
    <div className="flex items-center gap-2">
      <Badge className={studio.bank_verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
        {studio.bank_verified ? 'Verificado' : 'Pendente'}
      </Badge>
      <Button variant="ghost" disabled={mutation.isPending} onClick={() => mutation.mutate()}>
        {studio.bank_verified ? 'Revogar' : 'Verificar'}
      </Button>
    </div>
  )
}

export default function StudiosPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['admin-studios'],
    queryFn: adminApi.studios,
  })

  const studios = data ?? []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Studios</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && studios.length === 0 && (
        <p className="text-gray-500">Nenhum studio cadastrado.</p>
      )}

      {!isLoading && !isError && studios.length > 0 && (
        <>
          {/* Tabela (desktop) */}
          <Card className="hidden overflow-x-auto p-0 md:block">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-100 bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Nome</th>
                  <th className="px-4 py-3 font-medium">Slug</th>
                  <th className="px-4 py-3 font-medium">Dono</th>
                  <th className="px-4 py-3 font-medium">Plano</th>
                  <th className="px-4 py-3 font-medium">Agendamentos</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Banco</th>
                  <th className="px-4 py-3 font-medium">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {studios.map((s) => (
                  <tr key={s.id}>
                    <td className="px-4 py-3 font-medium text-gray-800">{s.name}</td>
                    <td className="px-4 py-3 text-gray-600">{s.slug}</td>
                    <td className="px-4 py-3 text-gray-600">{s.owner_email ?? '—'}</td>
                    <td className="px-4 py-3 capitalize text-gray-600">{s.plano}</td>
                    <td className="px-4 py-3 text-gray-600">{s.agendamentos_total}</td>
                    <td className="px-4 py-3">
                      <StatusBadge active={s.is_active} />
                    </td>
                    <td className="px-4 py-3">
                      <BancoCell studio={s} />
                    </td>
                    <td className="px-4 py-3">
                      <AcaoButton studio={s} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Cards (mobile) */}
          <div className="space-y-3 md:hidden">
            {studios.map((s) => (
              <Card key={s.id} className="space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-gray-800">{s.name}</p>
                    <p className="text-sm text-gray-600">/{s.slug}</p>
                  </div>
                  <StatusBadge active={s.is_active} />
                </div>
                <p className="text-sm text-gray-500">Dono: {s.owner_email ?? '—'}</p>
                <p className="text-sm capitalize text-gray-500">Plano: {s.plano}</p>
                <p className="text-sm text-gray-500">Agendamentos: {s.agendamentos_total}</p>
                <BancoCell studio={s} />
                <AcaoButton studio={s} />
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
