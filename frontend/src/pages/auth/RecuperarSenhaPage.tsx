import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Mail } from 'lucide-react'
import AuthShell from '@/components/AuthShell'
import { Button, Input, Field, ErrorMessage } from '@/components/ui'
import { authApi } from '@/api/auth'

export default function RecuperarSenhaPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState<unknown>(null)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await authApi.forgotPassword(email)
      setDone(true)
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  if (done) {
    return (
      <AuthShell title="Verifique seu email">
        <div className="text-center space-y-3">
          <Mail className="text-brand-500 mx-auto" size={56} />
          <p className="text-gray-600">
            Se existir uma conta com esse email, enviamos um link para redefinir a senha.
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
      title="Recuperar senha"
      subtitle="Enviaremos um link de redefinição"
      footer={
        <Link to="/auth/login" className="text-brand-600 font-medium">
          Voltar ao login
        </Link>
      }
    >
      <form onSubmit={submit} className="space-y-4">
        <Field label="Email">
          <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </Field>
        {error ? <ErrorMessage error={error} /> : null}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? 'Enviando...' : 'Enviar link'}
        </Button>
      </form>
    </AuthShell>
  )
}
