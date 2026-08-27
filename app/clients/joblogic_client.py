"""Central asynchronous HTTP client for verified JobLogic API operations."""

import logging
from typing import Any

import httpx

from app.config import Settings
from app.core.auth import JoblogicAuth, build_joblogic_headers
from app.core.exceptions import (
    JoblogicAPIError,
    JoblogicAuthenticationError,
    JoblogicTransportError,
)
from app.core.security import redact_headers

logger = logging.getLogger(__name__)


class JoblogicClient:
    """Owns shared HTTP behavior; resource services must use this client."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: httpx.AsyncClient | None = None
        self._auth_client: httpx.AsyncClient | None = None
        self._auth: JoblogicAuth | None = None

    async def start(self) -> None:
        """Create reusable HTTP clients during application startup."""

        if self._client is not None:
            return

        if self._settings.joblogic_base_url is None:
            logger.warning(
                "JobLogic base URL is not configured; remote calls are disabled"
            )
            return

        self._client = httpx.AsyncClient(
            base_url=str(self._settings.joblogic_base_url),
            timeout=self._settings.joblogic_timeout_seconds,
            headers=build_joblogic_headers(self._settings),
        )

        self._auth_client = httpx.AsyncClient(
            timeout=self._settings.joblogic_timeout_seconds
        )

        self._auth = JoblogicAuth(
            self._settings,
            self._auth_client,
        )

    async def close(self) -> None:
        """Close connections during application shutdown."""

        if self._client is not None:
            await self._client.aclose()
            self._client = None

        if self._auth_client is not None:
            await self._auth_client.aclose()
            self._auth_client = None
            self._auth = None

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | list[Any] | None = None,
    ) -> Any:
        """Execute a JobLogic API request."""

        if self._client is None:
            raise JoblogicTransportError(
                "JobLogic client is not configured. "
                "Set JOBLOGIC_BASE_URL first."
            )

        # Get OAuth token
        try:
            access_token = (
                await self._auth.get_access_token()
                if self._auth
                else None
            )
        except JoblogicAuthenticationError:
            raise

        if not access_token:
            raise JoblogicAuthenticationError(
                "JobLogic credentials are not configured."
            )

        try:
            response = await self._client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                headers=build_joblogic_headers(
                    self._settings,
                    access_token,
                ),
            )

        except httpx.HTTPError as exc:
            logger.exception(
                "Transport error while calling JobLogic: %s %s",
                method,
                path,
            )
            raise JoblogicTransportError(
                "JobLogic request failed"
            ) from exc

        # Get the raw response body BEFORE doing anything else.
        raw_text = response.text

        logger.info(
            "JobLogic response: method=%s path=%s status=%s body=%s",
            method,
            path,
            response.status_code,
            raw_text[:5000],
        )

        # Handle errors
        if response.is_error:

            body: Any

            if not raw_text:
                body = {
                    "status_code": response.status_code,
                    "message": "JobLogic returned an empty response body",
                }
            else:
                try:
                    body = response.json()
                except ValueError:
                    body = raw_text

            logger.error(
                "JobLogic API ERROR: status=%s body=%s",
                response.status_code,
                body,
            )

            raise JoblogicAPIError(
                status_code=response.status_code,
                detail=body,
                response_body=body,
            )

        # Successful response
        if response.status_code == 204 or not raw_text:
            return None

        try:
            return response.json()
        except ValueError:
            return raw_text