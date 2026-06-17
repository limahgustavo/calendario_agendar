import logging
import httpx
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class AsaasService:
    def __init__(self):
        self.headers = {
            "access_token": settings.ASAAS_API_KEY,
            "Content-Type": "application/json",
        }

    @property
    def base_url(self) -> str:
        return settings.ASAAS_BASE_URL

    async def _request(self, method: str, path: str, body: dict | None = None) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method, f"{self.base_url}{path}", json=body, headers=self.headers
            )
            if not resp.is_success:
                logger.error("Asaas %s %s -> %s: %s", method, path, resp.status_code, resp.text)
            resp.raise_for_status()
            return resp.json()

    async def _post(self, path: str, body: dict) -> dict[str, Any]:
        return await self._request("POST", path, body)

    # ---- Clientes ----
    async def find_or_create_customer(
        self, name: str, email: str, phone: str, cpf_cnpj: str | None = None
    ) -> str:
        """Retorna o ID do cliente no Asaas, criando ou atualizando se necessário."""
        cpf_digits = "".join(filter(str.isdigit, cpf_cnpj)) if cpf_cnpj else None

        async with httpx.AsyncClient(timeout=30) as client:
            search = await client.get(
                f"{self.base_url}/customers",
                params={"email": email},
                headers=self.headers,
            )
            search.raise_for_status()
            data = search.json()
            if data.get("data"):
                customer = data["data"][0]
                customer_id = customer["id"]
                if cpf_digits and not customer.get("cpfCnpj"):
                    await client.put(
                        f"{self.base_url}/customers/{customer_id}",
                        json={"cpfCnpj": cpf_digits},
                        headers=self.headers,
                    )
                return customer_id

        payload: dict[str, Any] = {"name": name, "email": email, "mobilePhone": phone}
        if cpf_digits:
            payload["cpfCnpj"] = cpf_digits
        result = await self._post("/customers", payload)
        return result["id"]

    # ---- Cobranças ----
    async def create_charge(
        self, customer_id: str, amount: float, description: str, due_date: str
    ) -> dict[str, Any]:
        """Cria cobrança (PIX/boleto/cartão) e retorna link e ID."""
        payload = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "value": round(amount, 2),
            "dueDate": due_date,
            "description": description,
            "externalReference": description,
        }
        result = await self._post("/payments", payload)
        return {
            "asaas_payment_id": result["id"],
            "asaas_invoice_url": result.get("invoiceUrl") or result.get("bankSlipUrl", ""),
        }

    # ---- Transferências (repasses) ----
    async def create_transfer(
        self, pix_key: str, value: float, description: str | None = None
    ) -> dict[str, Any]:
        """Transfere via PIX para a chave do studio. Retorna {asaas_transfer_id, status}."""
        payload: dict[str, Any] = {
            "value": round(value, 2),
            "pixAddressKey": pix_key,
            "operationType": "PIX",
        }
        if description:
            payload["description"] = description
        result = await self._post("/transfers", payload)
        return {"asaas_transfer_id": result.get("id"), "status": result.get("status")}

    # ---- Assinaturas (planos dos studios) ----
    async def create_subscription(
        self, customer_id: str, value: float, description: str, next_due_date: str
    ) -> dict[str, Any]:
        payload = {
            "customer": customer_id,
            "billingType": "UNDEFINED",
            "value": round(value, 2),
            "cycle": "MONTHLY",
            "description": description,
            "nextDueDate": next_due_date,
        }
        result = await self._post("/subscriptions", payload)
        return {"asaas_subscription_id": result.get("id"), "status": result.get("status")}


asaas_service = AsaasService()
