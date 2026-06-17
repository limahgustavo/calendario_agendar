import httpx

from app.core.config import settings


class ResendService:
    BASE_URL = "https://api.resend.com"

    async def send_email(self, to: str, subject: str, html: str) -> bool:
        if not settings.RESEND_API_KEY:
            return False
        payload = {
            "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
            "to": [to],
            "subject": subject,
            "html": html,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/emails",
                    json=payload,
                    headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}"},
                )
                resp.raise_for_status()
                return True
            except httpx.HTTPError:
                return False

    async def send_confirmation(
        self,
        to: str,
        client_name: str,
        service_name: str,
        scheduled_date: str,
        scheduled_time: str,
        total_price: float,
        deposit_amount: float,
        payment_link: str,
    ) -> bool:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #e91e8c;">Agendamento Confirmado! 💅</h2>
          <p>Olá, <strong>{client_name}</strong>!</p>
          <p>Seu agendamento foi registrado com sucesso.</p>
          <table style="width:100%; border-collapse: collapse; margin: 20px 0;">
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Serviço</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{service_name}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Data</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{scheduled_date}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Horário</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">{scheduled_time}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Valor total</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">R$ {total_price:.2f}</td></tr>
            <tr><td style="padding: 8px; border: 1px solid #ddd;"><strong>Sinal (50%)</strong></td>
                <td style="padding: 8px; border: 1px solid #ddd;">R$ {deposit_amount:.2f}</td></tr>
          </table>
          <p>
            <a href="{payment_link}"
               style="background:#e91e8c;color:#fff;padding:12px 24px;text-decoration:none;border-radius:6px;">
              Pagar Sinal (R$ {deposit_amount:.2f})
            </a>
          </p>
          <p style="color: #666; font-size: 14px;">
            O restante (R$ {total_price - deposit_amount:.2f}) é pago no local no dia do atendimento.
          </p>
        </div>
        """
        return await self.send_email(
            to, f"Agendamento confirmado — {service_name} em {scheduled_date}", html
        )

    async def send_reminder(
        self,
        to: str,
        client_name: str,
        service_name: str,
        scheduled_date: str,
        scheduled_time: str,
    ) -> bool:
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
          <h2 style="color: #e91e8c;">Lembrete de Agendamento ⏰</h2>
          <p>Olá, <strong>{client_name}</strong>!</p>
          <p>Este é um lembrete do seu agendamento:</p>
          <ul>
            <li><strong>Serviço:</strong> {service_name}</li>
            <li><strong>Data:</strong> {scheduled_date}</li>
            <li><strong>Horário:</strong> {scheduled_time}</li>
          </ul>
          <p>Te esperamos! 💅</p>
        </div>
        """
        return await self.send_email(
            to, f"Lembrete: {service_name} amanhã às {scheduled_time}", html
        )


resend_service = ResendService()
