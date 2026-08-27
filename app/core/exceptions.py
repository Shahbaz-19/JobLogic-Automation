"""Application exceptions and HTTP-safe error representations."""

from typing import Any


class JoblogicClientError(Exception):
    """Base exception raised for JobLogic communication failures."""


class JoblogicTransportError(JoblogicClientError):
    """The remote API could not be reached or timed out."""


class JoblogicAuthenticationError(JoblogicClientError):
    """JobLogic OAuth client-credentials authentication failed."""


class JoblogicAPIError(JoblogicClientError):
    """The JobLogic API returned an unsuccessful HTTP response."""

    def __init__(
        self,
        status_code: int,
        detail: Any,
        response_body: Any | None = None,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.response_body = response_body

        super().__init__(
            f"JobLogic API request failed with HTTP {status_code}: {detail}"
        )