import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ZAPIService:
    @property
    def base_url(self) -> str:
        # ZAPI_API_URL é a "API da instância" fornecida no painel Z-API
        api = settings.ZAPI_API_URL.rstrip("/")
        return f"{api}/instances/{settings.ZAPI_INSTANCE_ID}/token/{settings.ZAPI_TOKEN}"

    @property
    def headers(self) -> dict:
        return {"Client-Token": settings.ZAPI_CLIENT_TOKEN}

    def _format_phone(self, phone: str) -> str:
        digits = "".join(filter(str.isdigit, phone))
        if not digits.startswith("55"):
            digits = "55" + digits
        return digits

    async def send_text(self, phone: str, message: str) -> bool:
        if not settings.ZAPI_INSTANCE_ID or not settings.ZAPI_TOKEN:
            logger.warning("Z-API não configurado (ZAPI_INSTANCE_ID ou ZAPI_TOKEN vazio)")
            return False
        url = f"{self.base_url}/send-messages/send-text"
        payload = {"phone": self._format_phone(phone), "message": message}
        logger.info("Z-API send_text → %s phone=%s", url, self._format_phone(phone))
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                resp = await client.post(url, json=payload, headers=self.headers)
                if not resp.is_success:
                    logger.error("Z-API error %s: %s", resp.status_code, resp.text)
                resp.raise_for_status()
                return True
            except httpx.HTTPError as e:
                logger.error("Z-API HTTPError: %s", e)
                return False

    async def send_confirmation(
        self,
        phone: str,
        client_name: str,
        service_name: str,
        scheduled_date: str,  # DD/MM/YYYY
        scheduled_time: str,  # HH:MM
        total_price: float,
        confirm_url: str,
        cancel_url: str,
        reschedule_url: str,
        studio_name: str | None = None,
        payment_link: str | None = None,
    ) -> bool:
        local = f"\n📍 Local: {studio_name}" if studio_name else ""
        pay = f"\n\n💳 Pague para confirmar: {payment_link}" if payment_link else ""
        message = (
            f"Olá, {client_name}! 🎉\n\n"
            f"Seu agendamento foi registrado:\n"
            f"💅 Serviço: {service_name}{local}\n"
            f"📅 Data: {scheduled_date} às {scheduled_time}\n"
            f"💰 Valor: R$ {total_price:.2f}"
            f"{pay}\n\n"
            f"Gerencie seu agendamento:\n"
            f"✅ Confirmar: {confirm_url}\n"
            f"🔄 Remarcar: {reschedule_url}\n"
            f"❌ Cancelar: {cancel_url}"
        )
        return await self.send_text(phone, message)

    async def send_rating_request(
        self, phone: str, client_name: str, link: str, studio_name: str | None = None
    ) -> bool:
        local = f" no {studio_name}" if studio_name else ""
        message = (
            f"Oi, {client_name}! 💖\n\n"
            f"Obrigada pela visita{local}! Como foi seu atendimento?\n"
            f"Avalie de 1 a 5 estrelas aqui: {link}\n\n"
            f"Sua opinião ajuda muito! ✨"
        )
        return await self.send_text(phone, message)

    async def send_reminder(
        self,
        phone: str,
        client_name: str,
        service_name: str,
        scheduled_date: str,
        scheduled_time: str,
        hours_before: int,
        confirm_url: str,
        cancel_url: str,
        studio_name: str | None = None,
    ) -> bool:
        when = "AMANHÃ" if hours_before >= 20 else "em 2 HORAS"
        local = f" - {studio_name}" if studio_name else ""
        message = (
            f"Oi, {client_name}! Tudo bem? ⏰\n\n"
            f"Seu agendamento é {when}:\n"
            f"💅 {service_name}{local}\n"
            f"📅 {scheduled_date} às {scheduled_time}\n\n"
            f"✅ Confirmar: {confirm_url}\n"
            f"❌ Cancelar: {cancel_url}"
        )
        return await self.send_text(phone, message)


zapi_service = ZAPIService()
