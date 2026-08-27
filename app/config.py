"""Application settings loaded from environment variables."""

from functools import lru_cache

from uuid import UUID

from pydantic import AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration; secrets are never committed to source control."""

    app_name: str = "JobLogicAutomation"
    environment: str = "development"
    log_level: str = "INFO"
    joblogic_base_url: AnyHttpUrl | None = None
    joblogic_identity_url: AnyHttpUrl | None = None
    joblogic_tenant_id: UUID | None = None
    joblogic_client_id: str | None = None
    joblogic_client_secret: SecretStr | None = None
    joblogic_scope: str = "JL.Api"
    joblogic_api_token: SecretStr | None = None
    joblogic_api_key: SecretStr | None = None
    joblogic_api_key_header: str = "X-API-Key"
    joblogic_auth_scheme: str = "Bearer"
    joblogic_timeout_seconds: float = Field(default=30.0, gt=0, le=300)
    excel_input_file: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """Return one immutable settings instance for the running process."""

    return Settings()
