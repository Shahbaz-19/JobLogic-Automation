"""OAuth client-credentials authentication for Joblogic."""

from datetime import UTC, datetime, timedelta
import logging

import httpx

from app.config import Settings
from app.core.exceptions import JoblogicAuthenticationError

logger = logging.getLogger(__name__)


def build_joblogic_headers(settings: Settings, access_token: str | None = None) -> dict[str, str]:
    """Build non-secret request headers plus a supplied OAuth access token."""

    headers = {"Accept": "application/json"}
    token = access_token or (
        settings.joblogic_api_token.get_secret_value()
        if settings.joblogic_api_token
        else None
    )
    if token:
        headers["Authorization"] = f"{settings.joblogic_auth_scheme} {token}"
    if settings.joblogic_api_key:
        headers[settings.joblogic_api_key_header] = (
            settings.joblogic_api_key.get_secret_value()
        )
    return headers


class JoblogicAuth:
    """Obtains and refreshes a bearer token without persisting credentials."""

    _refresh_margin = timedelta(seconds=60)

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._client = client
        self._access_token: str | None = None
        self._expires_at: datetime | None = None

    async def get_access_token(self) -> str | None:
        """Return a configured static token or a valid client-credentials token."""

        if self._settings.joblogic_api_token:
            return self._settings.joblogic_api_token.get_secret_value()
        if not self._has_client_credentials():
            return None
        if self._access_token and self._expires_at:
            if datetime.now(UTC) < self._expires_at - self._refresh_margin:
                return self._access_token
        return await self._request_access_token()

    def _has_client_credentials(self) -> bool:
        return all(
            (
                self._settings.joblogic_identity_url,
                self._settings.joblogic_client_id,
                self._settings.joblogic_client_secret,
            )
        )

    async def _request_access_token(self) -> str:
        try:
            response = await self._client.post(
                str(self._settings.joblogic_identity_url),
                data={
                    "client_id": self._settings.joblogic_client_id,
                    "client_secret": self._settings.joblogic_client_secret.get_secret_value(),
                    "grant_type": "client_credentials",
                    "scope": self._settings.joblogic_scope,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            response.raise_for_status()
            payload = response.json()
            token = payload.get("access_token")
            if not isinstance(token, str) or not token:
                raise JoblogicAuthenticationError("Joblogic token response has no access token")
            expires_in = payload.get("expires_in", 3600)
            self._expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_in))
            self._access_token = token
            return token
        except (httpx.HTTPError, ValueError, TypeError) as exc:
            logger.warning("Joblogic OAuth token request failed")
            raise JoblogicAuthenticationError("Unable to authenticate with Joblogic") from exc
