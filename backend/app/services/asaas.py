import httpx
from typing import Any

from app.core.config import settings


class AsaasService:
    def __init__(self):
        self.base_url = settings.ASAAS_BASE_URL
        self.headers = {
            "access_token": settings.ASAAS_API_KEY,
            "Content-Type": "application/json",
        }

    async def _post(self, path: str, body: dict) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = client.post(f"{self.base_url}{path}", json=body, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def find_or_create_customer(self, name: str, email: str, phone: str) -> str:
        """Returns Asaas customer ID."""
        async with httpx.AsyncClient(timeout=30) as client:
            search = await client.get(
                f"{self.base_url}/customers",
                params={"email": email},
                headers=self.headers,
            )
            search.raise_for_status()
            data = search.json()
            if data.get("data"):
                return data["data"][0]["id"]

        result = await self._post(
            "/customers",
            {"name": name, "email": email, "mobilePhone": phone},
        )
        return result["id"]

    async def create_charge(
        self,
        customer_id: str,
        amount: float,
        description: str,
        due_date: str,  # YYYY-MM-DD
    ) -> dict[str, Any]:
        """Creates a charge and returns payment link and ID."""
        payload = {
            "customer": customer_id,
            "billingType": "UNDEFINED",  # cliente escolhe PIX/boleto/cartão
            "value": round(amount, 2),
            "dueDate": due_date,
            "description": description,
            "externalReference": description,
        }
        result = await self._post("/payments", payload)
        return {
            "asaas_payment_id": result["id"],
            "asaas_payment_link": result.get("invoiceUrl") or result.get("bankSlipUrl", ""),
            "asaas_invoice_url": result.get("invoiceUrl", ""),
        }


asaas_service = AsaasService()
