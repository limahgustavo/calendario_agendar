from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas

from app.models.appointment import Appointment
from app.models.studio import Studio
from app.models.payment import Payment
from app.models.enums import PaymentType

BRAND = (0.859, 0.153, 0.467)  # #db2777


def gerar_comprovante(appt: Appointment, studio: Studio, payment: Payment) -> bytes:
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    c.setFillColorRGB(*BRAND)
    c.rect(0, h - 2.2 * cm, w, 2.2 * cm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, h - 1.5 * cm, "Comprovante de Pagamento")

    c.setFillColorRGB(0.2, 0.2, 0.2)
    y = h - 3.5 * cm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, studio.name if studio else "Studio")

    tipo_label = {
        PaymentType.DEPOSIT: "Sinal (50%)",
        PaymentType.FULL: "Pagamento integral (100%)",
        PaymentType.REMAINDER: "Saldo restante",
    }.get(payment.tipo, "Pagamento")

    linhas = [
        ("Cliente", appt.client_name),
        ("Email", appt.client_email),
        ("Serviço", appt.servico_nome),
        ("Data do atendimento", f"{appt.data.strftime('%d/%m/%Y')} às {appt.hora}"),
        ("Valor pago", f"R$ {float(payment.valor):.2f}"),
        ("Tipo", tipo_label),
        ("Valor total do serviço", f"R$ {float(appt.preco):.2f}"),
        ("Status", "Confirmado"),
        ("Pago em", payment.paid_at.strftime("%d/%m/%Y %H:%M") if payment.paid_at else "-"),
        ("Comprovante nº", str(payment.id)),
    ]

    y -= 1 * cm
    for label, value in linhas:
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.45, 0.45, 0.45)
        c.drawString(2 * cm, y, label)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColorRGB(0.1, 0.1, 0.1)
        c.drawString(8 * cm, y, str(value))
        y -= 0.8 * cm

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColorRGB(0.6, 0.6, 0.6)
    c.drawString(2 * cm, 2 * cm, "Gerado por NailBook — este documento comprova o pagamento acima.")

    c.showPage()
    c.save()
    return buf.getvalue()
