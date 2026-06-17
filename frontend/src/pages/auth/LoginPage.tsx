import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import AuthShell from '@/components/AuthShell'
import { Button, Input, Field, ErrorMessage } from '@/components/ui'
import { useAuth, homeForRole } from '@/hooks/useAuth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const role = await login(email, password)
      navigate(homeForRole(role))
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell
      title="Entrar"
      footer={
        <>
          Não tem conta?{' '}
          <Link to="/auth/registro" className="text-brand-600 font-medium">
            Criar conta
          </Link>{' '}
          ·{' '}
          <Link to="/auth/studio" className="text-brand-600 font-medium">
            Sou nail designer
          </Link>
        </>
      }
    >
      <form onSubmit={submit} className="space-y-4">
        <Field label="Email">
          <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </Field>
        <Field label="Senha">
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </Field>
        {error ? <ErrorMessage error={error} /> : null}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? 'Entrando...' : 'Entrar'}
        </Button>
        <Link to="/auth/recuperar" className="block text-center text-sm text-gray-500 hover:underline">
          Esqueci minha senha
        </Link>
      </form>
    </AuthShell>
  )
}
