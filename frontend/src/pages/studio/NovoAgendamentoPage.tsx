import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { servicesApi } from '@/api/services'
import { appointmentsApi } from '@/api/appointments'
import { Button, Input, Select, Field, Card, Spinner, ErrorMessage } from '@/components/ui'
import { formatCurrency } from '@/lib/utils'

export default function NovoAgendamentoPage() {
  const servicesQuery = useQuery({ queryKey: ['services'], queryFn: servicesApi.list })

  const [form, setForm] = useState({
    service_id: '',
    data: '',
    hora: '',
    client_name: '',
    client_email: '',
    client_phone: '',
    client_cpf_cnpj: '',
  })
  const [cobrar, setCobrar] = useState(true)
  const [copied, setCopied] = useState(false)

  const mutation = useMutation({
    mutationFn: () =>
      appointmentsApi.createManual({
        service_id: form.service_id,
        data: form.data,
        hora: form.hora,
        client_name: form.client_name,
        client_email: form.client_email,
        client_phone: form.client_phone,
        client_cpf_cnpj: form.client_cpf_cnpj || undefined,
        cobrar,
      }),
  })

  const copyLink = async (link: string) => {
    await navigator.clipboard.writeText(link)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const services = (servicesQuery.data ?? []).filter((s) => s.is_active)

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Novo agendamento</h1>

      {mutation.isSuccess ? (
        <Card className="space-y-4">
          <p className="font-semibold text-green-700">{mutation.data.message}</p>
          <p className="text-gray-600">
            Valor: <span className="font-semibold">{formatCurrency(mutation.data.amount)}</span>
          </p>
          {mutation.data.payment_link && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">Link de pagamento</p>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
                <a
                  href={mutation.data.payment_link}
                  target="_blank"
                  rel="noreferrer"
                  className="flex-1 break-all rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-brand-600 hover:underline"
                >
                  {mutation.data.payment_link}
                </a>
                <Button variant="secondary" onClick={() => copyLink(mutation.data.payment_link)}>
                  {copied ? 'Copiado!' : 'Copiar'}
                </Button>
              </div>
            </div>
          )}
          <Link to="/studio/agendamentos" className="inline-block text-brand-600 hover:underline">
            ← Voltar para agendamentos
          </Link>
        </Card>
      ) : (
        <Card>
          {servicesQuery.isLoading && <Spinner />}
          {servicesQuery.isError && <ErrorMessage error={servicesQuery.error} />}

          {!servicesQuery.isLoading && !servicesQuery.isError && (
            <form
              onSubmit={(e: FormEvent) => {
                e.preventDefault()
                mutation.mutate()
              }}
              className="space-y-4"
            >
              <Field label="Serviço">
                <Select
                  value={form.service_id}
                  onChange={(e) => setForm({ ...form, service_id: e.target.value })}
                  required
                >
                  <option value="" disabled>
                    Selecione um serviço
                  </option>
                  {services.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} — {formatCurrency(s.price)}
                    </option>
                  ))}
                </Select>
              </Field>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Field label="Data">
                  <Input
                    type="date"
                    value={form.data}
                    onChange={(e) => setForm({ ...form, data: e.target.value })}
                    required
                  />
                </Field>
                <Field label="Horário">
                  <Input
                    type="time"
                    value={form.hora}
                    onChange={(e) => setForm({ ...form, hora: e.target.value })}
                    required
                  />
                </Field>
              </div>

              <Field label="Nome do cliente">
                <Input
                  value={form.client_name}
                  onChange={(e) => setForm({ ...form, client_name: e.target.value })}
                  required
                />
              </Field>
              <Field label="Email do cliente">
                <Input
                  type="email"
                  value={form.client_email}
                  onChange={(e) => setForm({ ...form, client_email: e.target.value })}
                  required
                />
              </Field>
              <Field label="WhatsApp do cliente">
                <Input
                  value={form.client_phone}
                  onChange={(e) => setForm({ ...form, client_phone: e.target.value })}
                  placeholder="(11) 99999-9999"
                  required
                />
              </Field>
              <Field label="CPF ou CNPJ (opcional)">
                <Input
                  value={form.client_cpf_cnpj}
                  onChange={(e) => setForm({ ...form, client_cpf_cnpj: e.target.value })}
                  placeholder="000.000.000-00"
                />
              </Field>

              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={cobrar}
                  onChange={(e) => setCobrar(e.target.checked)}
                  className="h-4 w-4 rounded border-gray-300 text-brand-600 focus:ring-brand-400"
                />
                Gerar cobrança agora
              </label>

              {mutation.isError && <ErrorMessage error={mutation.error} />}

              <Button type="submit" disabled={mutation.isPending} className="w-full">
                {mutation.isPending ? 'Aguarde...' : 'Criar agendamento'}
              </Button>
            </form>
          )}
        </Card>
      )}
    </div>
  )
}
