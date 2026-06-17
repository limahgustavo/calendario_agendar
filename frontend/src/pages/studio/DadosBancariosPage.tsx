import { useState, useEffect, type FormEvent } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { studiosApi } from '@/api/studios'
import { Button, Input, Select, Field, Card, Spinner, ErrorMessage } from '@/components/ui'
import type { PaymentMode } from '@/types'

export default function DadosBancariosPage() {
  const queryClient = useQueryClient()
  const { data: studio, isLoading, isError, error } = useQuery({
    queryKey: ['my-studio'],
    queryFn: studiosApi.me,
  })

  const [paymentMode, setPaymentMode] = useState<PaymentMode>('deposit_50')
  const [pixKey, setPixKey] = useState('')
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (studio) {
      setPaymentMode(studio.payment_mode)
      setPixKey(studio.pix_key ?? '')
    }
  }, [studio])

  const mutation = useMutation({
    mutationFn: () => studiosApi.update({ payment_mode: paymentMode, pix_key: pixKey }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-studio'] })
      setSaved(true)
    },
  })

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Recebimento</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && studio && (
        <Card>
          <p className="mb-4 text-sm text-gray-600">
            Os repasses semanais caem nesta chave PIX, já descontada a taxa da plataforma.
          </p>

          <form
            onSubmit={(e: FormEvent) => {
              e.preventDefault()
              mutation.mutate()
            }}
            className="space-y-4"
          >
            <Field label="Modo de cobrança">
              <Select
                value={paymentMode}
                onChange={(e) => {
                  setSaved(false)
                  setPaymentMode(e.target.value as PaymentMode)
                }}
              >
                <option value="deposit_50">Cobrar 50% (sinal)</option>
                <option value="full_100">Cobrar 100% antecipado</option>
              </Select>
            </Field>

            <Field label="Chave PIX">
              <Input
                value={pixKey}
                onChange={(e) => {
                  setSaved(false)
                  setPixKey(e.target.value)
                }}
                placeholder="CPF, e-mail, telefone ou chave aleatória"
              />
            </Field>

            {mutation.isError && <ErrorMessage error={mutation.error} />}
            {saved && <p className="text-sm font-medium text-green-700">Dados salvos com sucesso!</p>}

            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Salvando...' : 'Salvar'}
            </Button>
          </form>
        </Card>
      )}
    </div>
  )
}
