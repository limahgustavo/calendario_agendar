import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { authApi } from '@/api/auth'
import { Button, Input, Field, Card, Spinner, ErrorMessage } from '@/components/ui'

export default function PerfilPage() {
  const queryClient = useQueryClient()
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['me'],
    queryFn: authApi.me,
  })

  const [name, setName] = useState('')
  const [whatsapp, setWhatsapp] = useState('')
  const [celular, setCelular] = useState('')
  const [cpfCnpj, setCpfCnpj] = useState('')
  const [showSuccess, setShowSuccess] = useState(false)

  useEffect(() => {
    if (data) {
      setName(data.name)
      setWhatsapp(data.whatsapp ?? '')
      setCelular(data.celular ?? '')
      setCpfCnpj(data.cpf_cnpj ?? '')
    }
  }, [data])

  useEffect(() => {
    if (!showSuccess) return
    const timer = setTimeout(() => setShowSuccess(false), 3000)
    return () => clearTimeout(timer)
  }, [showSuccess])

  const mutation = useMutation({
    mutationFn: authApi.updateMe,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['me'] })
      setShowSuccess(true)
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    mutation.mutate({
      name,
      whatsapp: whatsapp || null,
      celular: celular || null,
      cpf_cnpj: cpfCnpj || null,
    })
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Meu perfil</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && data && (
        <Card>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Field label="Nome">
              <Input value={name} onChange={(e) => setName(e.target.value)} required />
            </Field>

            <Field label="E-mail">
              <Input value={data.email} disabled />
            </Field>

            <Field label="WhatsApp">
              <Input value={whatsapp} onChange={(e) => setWhatsapp(e.target.value)} />
            </Field>

            <Field label="Celular">
              <Input value={celular} onChange={(e) => setCelular(e.target.value)} />
            </Field>

            <Field label="CPF/CNPJ">
              <Input value={cpfCnpj} onChange={(e) => setCpfCnpj(e.target.value)} />
            </Field>

            {mutation.isError && <ErrorMessage error={mutation.error} />}
            {showSuccess && (
              <p className="text-sm bg-green-50 border border-green-200 text-green-700 rounded-xl p-3">
                Perfil atualizado!
              </p>
            )}

            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Salvando...' : 'Salvar'}
            </Button>
          </form>
        </Card>
      )}
    </div>
  )
}
