from typing import Any

from app.clients.joblogic_client import JoblogicClient
from app.config import Settings


class StaffService:
    """JobLogic Staff API operations."""

    def __init__(
        self,
        settings: Settings,
        client: JoblogicClient,
    ) -> None:
        self._settings = settings
        self._client = client

    async def get_all_staff(
        self,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        """POST /api/v1/staff/GetAll"""
        return await self._client.request(
            "POST",
            "/staff/GetAll",
            json=payload or {},
        )

    async def get_staff_by_unique_id(
        self,
        unique_id: str,
        tenant_id: str,
    ) -> Any:
        """GET /api/v1/staff?uniqueId=<UniqueId>&tenantId=<TenantId>"""
        # Try both parameter spellings to guarantee compatibility with all JobLogic environments
        try:
            return await self._client.request(
                "GET",
                "/staff",
                params={
                    "uniqueId": unique_id,
                    "tenantId": tenant_id,
                },
            )
        except Exception:
            return await self._client.request(
                "GET",
                "/staff",
                params={
                    "uniqiueid": unique_id,
                    "tenantId": tenant_id,
                },
            )
