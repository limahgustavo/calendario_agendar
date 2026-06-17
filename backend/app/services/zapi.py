import httpx

from app.core.config import settings


class ZAPIService:
    @property
    def base_url(self) -> str:
        return (
            f"https://api.z-api.io/instances/{settings.ZAPI_INSTANCE_ID}"
            f"/token/{settings.ZAPI_TOKEN}"
        )

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
            return False
        payload = {"phone": self._format_phone(phone), "message": message}
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/send-messages/send-text",
                    json=payload,
                    headers=self.headers,
                )
                resp.raise_for_status()
                return True
            except httpx.HTTPError:
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
    ) -> bool:
        message = (
            f"Olá, {client_name}! ✅\n\n"
            f"Seu agendamento foi confirmado:\n"
            f"💅 Serviço: {service_name}\n"
            f"📅 Data: {scheduled_date} às {scheduled_time}\n"
            f"💰 Total: R$ {total_price:.2f}\n\n"
            f"Acesse os links abaixo:\n"
            f"✅ Confirmar: {confirm_url}\n"
            f"🔄 Remarcar: {reschedule_url}\n"
            f"❌ Cancelar: {cancel_url}"
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
    ) -> bool:
        when = "AMANHÃ" if hours_before >= 20 else "em breve"
        message = (
            f"Oi, {client_name}! Tudo bem? ⏰\n\n"
            f"Seu agendamento é {when}:\n"
            f"💅 {service_name}\n"
            f"📅 {scheduled_date} às {scheduled_time}\n\n"
            f"✅ Confirmar: {confirm_url}\n"
            f"❌ Cancelar: {cancel_url}"
        )
        return await self.send_text(phone, message)


zapi_service = ZAPIService()
