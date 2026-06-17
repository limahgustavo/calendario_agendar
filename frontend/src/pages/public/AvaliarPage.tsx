import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Star, CheckCircle } from 'lucide-react'
import { appointmentsApi } from '@/api/appointments'
import { Button, Spinner, ErrorMessage } from '@/components/ui'
import { cn, formatDateShort } from '@/lib/utils'

export default function AvaliarPage() {
  const { token = '' } = useParams()
  const navigate = useNavigate()
  const [rating, setRating] = useState(0)
  const [hover, setHover] = useState(0)
  const [comment, setComment] = useState('')

  const { data, isLoading, isError } = useQuery({
    queryKey: ['rating-info', token],
    queryFn: () => appointmentsApi.ratingInfo(token),
  })

  const mutation = useMutation({
    mutationFn: () => appointmentsApi.submitRating(token, rating, comment || undefined),
  })

  if (isLoading) return <Spinner />
  if (isError || !data)
    return (
      <div className="min-h-screen flex items-center justify-center text-gray-500">
        Agendamento não encontrado.
      </div>
    )

  const alreadyRated = data.rating != null && !mutation.isSuccess

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 to-white flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-lg p-8 text-center space-y-6">
        {mutation.isSuccess || alreadyRated ? (
          <>
            <CheckCircle className="text-green-500 mx-auto" size={64} />
            <h1 className="text-2xl font-bold text-gray-800">Obrigada pela avaliação! 💖</h1>
            <p className="text-gray-500">Sua opinião nos ajuda muito.</p>
            <Button onClick={() => navigate('/')} className="w-full">
              Início
            </Button>
          </>
        ) : (
          <>
            <div>
              <h1 className="text-2xl font-bold text-brand-700">Como foi seu atendimento?</h1>
              <p className="text-gray-500 mt-2">
                {data.servico_nome}
                {data.studio_name ? ` · ${data.studio_name}` : ''}
                <br />
                {formatDateShort(data.data)} às {data.hora}
              </p>
            </div>

            <div className="flex justify-center gap-2">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  onMouseEnter={() => setHover(n)}
                  onMouseLeave={() => setHover(0)}
                  onClick={() => setRating(n)}
                  aria-label={`${n} estrelas`}
                >
                  <Star
                    size={40}
                    className={cn(
                      'transition-colors',
                      (hover || rating) >= n
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300',
                    )}
                  />
                </button>
              ))}
            </div>

            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={3}
              placeholder="Deixe um comentário (opcional)"
              className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-400 resize-none"
            />

            {mutation.isError ? <ErrorMessage error={mutation.error} /> : null}

            <Button
              onClick={() => mutation.mutate()}
              disabled={rating === 0 || mutation.isPending}
              className="w-full py-3 text-lg disabled:opacity-50"
            >
              {mutation.isPending ? 'Enviando...' : 'Enviar avaliação'}
            </Button>
          </>
        )}
      </div>
    </div>
  )
}
