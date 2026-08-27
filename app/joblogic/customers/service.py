from typing import Any

from app.clients.joblogic_client import JoblogicClient
from app.config import Settings


class CustomerService:
    def __init__(
        self,
        settings: Settings,
        client: JoblogicClient,
    ) -> None:
        self._settings = settings
        self._client = client

    async def create_customer(
        self,
        payload: dict[str, Any],
    ) -> Any:
        return await self._client.request(
            "POST",
            "/Customer",
            json=payload,
        )

    async def get_all_customers(
        self,
        payload: dict[str, Any],
    ) -> Any:
        return await self._client.request(
            "POST",
            "/Customer/GetAll",
            json=payload,
        )

    async def get_customer_by_id(
        self,
        customer_id: int,
        include_additional_details: bool,
        tenant_id: str,
    ) -> Any:
        return await self._client.request(
            "GET",
            "/Customer/GetById",
            params={
                "id": customer_id,
                "includeAdditionalDetails": include_additional_details,
                "tenantId": tenant_id,
            },
        )
    