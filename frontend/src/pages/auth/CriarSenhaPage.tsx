import { useState, type FormEvent } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import AuthShell from '@/components/AuthShell'
import { Button, Input, Field, ErrorMessage } from '@/components/ui'
import { authApi } from '@/api/auth'
import { useAuth, homeForRole } from '@/hooks/useAuth'

export default function CriarSenhaPage() {
  const { token = '' } = useParams()
  const navigate = useNavigate()
  const { setSession } = useAuth()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()
    if (password !== confirm) {
      setError(new Error('As senhas não conferem.'))
      return
    }
    setLoading(true)
    setError(null)
    try {
      const res = await authApi.setPassword(token, password)
      setSession(res.access_token, res.role)
      navigate(homeForRole(res.role))
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <AuthShell title="Criar senha" subtitle="Defina sua senha de acesso">
      <form onSubmit={submit} className="space-y-4">
        <Field label="Nova senha">
          <Input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={6}
          />
        </Field>
        <Field label="Confirmar senha">
          <Input
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            required
            minLength={6}
          />
        </Field>
        {error ? <ErrorMessage error={error} /> : null}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? 'Salvando...' : 'Criar senha e entrar'}
        </Button>
      </form>
    </AuthShell>
  )
}
