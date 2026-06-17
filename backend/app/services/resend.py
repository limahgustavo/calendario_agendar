import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ResendService:
    BASE_URL = "https://api.resend.com"

    async def send_email(self, to: str, subject: str, html: str) -> bool:
        if not settings.RESEND_API_KEY:
            logger.warning("Resend não configurado (RESEND_API_KEY vazia)")
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
                if not resp.is_success:
                    logger.error("Resend erro %s (to=%s): %s", resp.status_code, to, resp.text)
                resp.raise_for_status()
                return True
            except httpx.HTTPError as e:
                logger.error("Resend HTTPError (to=%s): %s", to, e)
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

    def _button(self, url: str, label: str) -> str:
        return (
            f'<a href="{url}" style="background:#db2777;color:#fff;padding:12px 24px;'
            f'text-decoration:none;border-radius:8px;display:inline-block;">{label}</a>'
        )

    def _wrap(self, inner: str) -> str:
        return (
            '<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">'
            f"{inner}</div>"
        )

    async def send_set_password(self, to: str, name: str, link: str) -> bool:
        html = self._wrap(
            f'<h2 style="color:#db2777;">Bem-vinda! 💅</h2>'
            f"<p>Olá, <strong>{name}</strong>!</p>"
            "<p>Sua conta foi criada. Clique no botão abaixo para definir sua senha "
            "e acessar seus agendamentos:</p>"
            f"<p>{self._button(link, 'Criar minha senha')}</p>"
            '<p style="color:#666;font-size:13px;">O link expira em 48 horas.</p>'
        )
        return await self.send_email(to, "Crie sua senha de acesso", html)

    async def send_reset_password(self, to: str, name: str, link: str) -> bool:
        html = self._wrap(
            f'<h2 style="color:#db2777;">Redefinir senha</h2>'
            f"<p>Olá, <strong>{name}</strong>!</p>"
            "<p>Recebemos um pedido para redefinir sua senha. Clique abaixo:</p>"
            f"<p>{self._button(link, 'Redefinir senha')}</p>"
            '<p style="color:#666;font-size:13px;">Se não foi você, ignore este email. '
            "O link expira em 2 horas.</p>"
        )
        return await self.send_email(to, "Redefinir sua senha", html)

    async def send_balance_notice(
        self, to: str, name: str, valor_restante: float, service_name: str, studio_name: str
    ) -> bool:
        html = self._wrap(
            f'<h2 style="color:#db2777;">Saldo do seu atendimento</h2>'
            f"<p>Olá, <strong>{name}</strong>!</p>"
            f"<p>Referente ao seu atendimento de <strong>{service_name}</strong> em "
            f"<strong>{studio_name}</strong>, há um saldo de "
            f"<strong>R$ {valor_restante:.2f}</strong> a ser pago presencialmente no studio.</p>"
        )
        return await self.send_email(to, "Saldo do seu atendimento", html)

    async def send_payout_notice(self, to: str, name: str, valor_liquido: float) -> bool:
        html = self._wrap(
            f'<h2 style="color:#db2777;">Repasse aprovado ✅</h2>'
            f"<p>Olá, <strong>{name}</strong>!</p>"
            f"<p>Um repasse de <strong>R$ {valor_liquido:.2f}</strong> foi aprovado e "
            "transferido para sua conta via PIX.</p>"
        )
        return await self.send_email(to, "Seu repasse foi aprovado", html)

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
