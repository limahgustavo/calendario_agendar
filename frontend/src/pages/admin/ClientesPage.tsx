import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '@/api/admin'
import { Button, Card, Badge, Spinner, ErrorMessage } from '@/components/ui'
import type { ClientRow } from '@/types'

function StatusBadge({ active }: { active: boolean }) {
  return (
    <Badge className={active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
      {active ? 'Ativo' : 'Bloqueado'}
    </Badge>
  )
}

function AcaoButton({ client }: { client: ClientRow }) {
  const queryClient = useQueryClient()
  const mutation = useMutation({
    mutationFn: () => adminApi.blockClient(client.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-clients'] })
    },
  })

  return (
    <Button
      variant={client.is_active ? 'secondary' : 'primary'}
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      {client.is_active ? 'Bloquear' : 'Reativar'}
    </Button>
  )
}

export default function ClientesPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['admin-clients'],
    queryFn: adminApi.clients,
  })

  const clients = data ?? []

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Clientes</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && clients.length === 0 && (
        <p className="text-gray-500">Nenhum cliente cadastrado.</p>
      )}

      {!isLoading && !isError && clients.length > 0 && (
        <>
          {/* Tabela (desktop) */}
          <Card className="hidden overflow-x-auto p-0 md:block">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-100 bg-gray-50 text-gray-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Nome</th>
                  <th className="px-4 py-3 font-medium">Email</th>
                  <th className="px-4 py-3 font-medium">WhatsApp</th>
                  <th className="px-4 py-3 font-medium">Agendamentos</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {clients.map((c) => (
                  <tr key={c.id}>
                    <td className="px-4 py-3 font-medium text-gray-800">{c.name}</td>
                    <td className="px-4 py-3 text-gray-600">{c.email}</td>
                    <td className="px-4 py-3 text-gray-600">{c.whatsapp ?? '—'}</td>
                    <td className="px-4 py-3 text-gray-600">{c.total_agendamentos}</td>
                    <td className="px-4 py-3">
                      <StatusBadge active={c.is_active} />
                    </td>
                    <td className="px-4 py-3">
                      <AcaoButton client={c} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          {/* Cards (mobile) */}
          <div className="space-y-3 md:hidden">
            {clients.map((c) => (
              <Card key={c.id} className="space-y-2">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-bold text-gray-800">{c.name}</p>
                    <p className="text-sm text-gray-600">{c.email}</p>
                  </div>
                  <StatusBadge active={c.is_active} />
                </div>
                <p className="text-sm text-gray-500">WhatsApp: {c.whatsapp ?? '—'}</p>
                <p className="text-sm text-gray-500">Agendamentos: {c.total_agendamentos}</p>
                <AcaoButton client={c} />
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
