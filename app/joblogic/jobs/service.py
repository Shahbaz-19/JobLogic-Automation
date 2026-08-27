from typing import Any

from app.clients.joblogic_client import JoblogicClient
from app.config import Settings


class JobService:
    """
    JobLogic job-related API operations.
    """

    def __init__(
        self,
        settings: Settings,
        client: JoblogicClient,
    ) -> None:
        self._settings = settings
        self._client = client

    # ============================================================
    # CREATE JOB
    # ============================================================

    async def create_job(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return await self._client.request(
            "POST",
            "/Job",
            json=payload,
        )

    # ============================================================
    # CREATE JOB NOTE
    # ============================================================

    async def create_note(
        self,
        payload: dict[str, Any],
    ) -> Any:
        """Create a note against an existing JobLogic entity."""

        return await self._client.request(
            "POST",
            "/Note",
            json=payload,
        )

    # ============================================================
    # SEARCH JOBS
    # ============================================================

    async def search_jobs(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return await self._client.request(
            "POST",
            "/Job/getall",
            json=payload,
        )

    # ============================================================
    # SEARCH JOB TYPES
    # ============================================================

    async def search_job_types(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return await self._client.request(
            "POST",
            "/jobtype/GetAll",
            json=payload,
        )

    # ============================================================
    # SEARCH JOB CATEGORIES
    # ============================================================

    async def search_job_categories(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return await self._client.request(
            "POST",
            "/JobCategory/GetAll",
            json=payload,
        )

    # ============================================================
    # SEARCH PRIORITIES
    # ============================================================

    async def search_priorities(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return await self._client.request(
            "POST",
            "/Priority/GetAll",
            json=payload,
        )

    # ============================================================
    # SEARCH TRADES
    # ============================================================

    async def search_trades(
        self,
        payload: dict[str, Any],
    ) -> Any:

        return await self._client.request(
            "POST",
            "/Trade/GetAll",
            json=payload,
        )