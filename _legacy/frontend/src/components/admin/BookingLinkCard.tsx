import { useState } from 'react'
import { Copy, Download, Check, Link } from 'lucide-react'

export default function BookingLinkCard() {
  const [copied, setCopied] = useState(false)

  const bookingUrl = `${window.location.origin}/`
  const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&color=be185d&data=${encodeURIComponent(bookingUrl)}`

  function copyLink() {
    navigator.clipboard.writeText(bookingUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  function downloadQR() {
    const a = document.createElement('a')
    a.href = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&color=be185d&data=${encodeURIComponent(bookingUrl)}`
    a.download = 'qrcode-agendamento.png'
    a.target = '_blank'
    a.click()
  }

  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="flex items-center gap-2 mb-4">
        <Link size={18} className="text-brand-600" />
        <h2 className="font-semibold text-gray-700">Link de Agendamento</h2>
      </div>

      <div className="flex flex-col sm:flex-row gap-6 items-center">
        <div className="flex-shrink-0 p-3 bg-white border-2 border-gray-100 rounded-xl">
          <img src={qrUrl} alt="QR Code de agendamento" width={150} height={150} />
        </div>

        <div className="flex-1 space-y-3 w-full">
          <p className="text-sm text-gray-500">
            Compartilhe este link ou QR code com suas clientes para que possam agendar diretamente.
          </p>

          <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2">
            <span className="text-sm text-gray-700 flex-1 truncate">{bookingUrl}</span>
            <button
              onClick={copyLink}
              className="flex items-center gap-1 text-xs px-3 py-1.5 bg-brand-600 text-white rounded-lg hover:bg-brand-700 transition-colors shrink-0"
            >
              {copied ? <Check size={13} /> : <Copy size={13} />}
              {copied ? 'Copiado!' : 'Copiar'}
            </button>
          </div>

          <button
            onClick={downloadQR}
            className="flex items-center gap-2 text-sm px-4 py-2 border border-brand-300 text-brand-700 rounded-xl hover:bg-brand-50 transition-colors"
          >
            <Download size={15} />
            Baixar QR Code
          </button>
        </div>
      </div>
    </div>
  )
}
