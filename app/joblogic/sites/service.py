from typing import Any

from app.clients.joblogic_client import JoblogicClient
from app.config import Settings


class SiteService:
    def __init__(
        self,
        settings: Settings,
        client: JoblogicClient,
    ) -> None:
        self._settings = settings
        self._client = client

    async def get_all_sites(
        self,
        payload: dict[str, Any],
    ) -> Any:
        return await self._client.request(
            "POST",
            "/Site/GetAll",
            params={
                "tenantId": payload["TenantId"],
            },
            json=payload,
        )

    async def create_site(
        self,
        payload: dict[str, Any],
    ) -> Any:
        return await self._client.request(
            "POST",
            "/Site",
            params={
                "tenantId": payload["TenantId"],
            },
            json=payload,
        )