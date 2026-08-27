"""Resource-independent integration service."""

from app.config import Settings
from app.joblogic.base.schemas import HealthResponse


class BaseService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def health(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            environment=self._settings.environment,
            joblogic_configured=self._settings.joblogic_base_url is not None,
        )
