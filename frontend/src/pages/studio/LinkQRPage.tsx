import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { studiosApi } from '@/api/studios'
import { Button, Card, Spinner, ErrorMessage } from '@/components/ui'

export default function LinkQRPage() {
  const { data: studio, isLoading, isError, error } = useQuery({
    queryKey: ['my-studio'],
    queryFn: studiosApi.me,
  })
  const [copied, setCopied] = useState(false)

  const copyLink = async (url: string) => {
    await navigator.clipboard.writeText(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Link & QR Code</h1>

      {isLoading && <Spinner />}
      {isError && <ErrorMessage error={error} />}

      {!isLoading && !isError && studio && (() => {
        const bookingUrl = `${window.location.origin}/booking/${studio.slug}`
        const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=240x240&data=${encodeURIComponent(
          bookingUrl,
        )}`

        return (
          <>
            <Card className="space-y-3">
              <p className="text-gray-600">
                Compartilhe este link para que suas clientes agendem sozinhas, sem precisar criar
                uma conta.
              </p>
              <a
                href={bookingUrl}
                target="_blank"
                rel="noreferrer"
                className="block break-all rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-brand-600 hover:underline"
              >
                {bookingUrl}
              </a>
              <Button onClick={() => copyLink(bookingUrl)}>
                {copied ? 'Copiado!' : 'Copiar link'}
              </Button>
            </Card>

            <Card className="space-y-4 text-center">
              <h2 className="text-lg font-semibold text-gray-700">QR Code</h2>
              <img
                src={qrUrl}
                alt="QR Code do link de agendamento"
                width={240}
                height={240}
                className="mx-auto rounded-xl border border-gray-100"
              />
              <a href={qrUrl} download="qrcode-agendamento.png" className="inline-block">
                <Button variant="secondary">Baixar QR</Button>
              </a>
            </Card>
          </>
        )
      })()}
    </div>
  )
}
