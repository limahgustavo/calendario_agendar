import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'
import AuthShell from '@/components/AuthShell'
import { Button, Input, Field, ErrorMessage } from '@/components/ui'
import { authApi } from '@/api/auth'

export default function RegistroPage() {
  const [form, setForm] = useState({ name: '', email: '', whatsapp: '' })
  const [error, setError] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await authApi.register(form)
      setDone(true)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  if (done) {
    return (
      <AuthShell title="Quase lá!">
        <div className="text-center space-y-3">
          <CheckCircle className="text-green-500 mx-auto" size={56} />
          <p className="text-gray-600">
            Enviamos um link para <strong>{form.email}</strong> criar sua senha. Confira seu email.
          </p>
          <Link to="/auth/login" className="text-brand-600 font-medium block">
            Voltar ao login
          </Link>
        </div>
      </AuthShell>
    )
  }

  return (
    <AuthShell
      title="Criar conta"
      subtitle="Para agendar e acompanhar seus horários"
      footer={
        <>
          Já tem conta?{' '}
          <Link to="/auth/login" className="text-brand-600 font-medium">
            Entrar
          </Link>
        </>
      }
    >
      <form onSubmit={submit} className="space-y-4">
        <Field label="Nome completo">
          <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        </Field>
        <Field label="Email">
          <Input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />
        </Field>
        <Field label="WhatsApp">
          <Input
            value={form.whatsapp}
            onChange={(e) => setForm({ ...form, whatsapp: e.target.value })}
            placeholder="(11) 99999-9999"
          />
        </Field>
        {error ? <ErrorMessage error={error} /> : null}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? 'Enviando...' : 'Criar conta'}
        </Button>
      </form>
    </AuthShell>
  )
}
