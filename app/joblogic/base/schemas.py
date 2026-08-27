"""Schemas for infrastructure status responses."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    environment: str
    joblogic_configured: bool
