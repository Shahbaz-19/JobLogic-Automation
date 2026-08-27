"""Infrastructure-only API routes."""

from fastapi import APIRouter, Request

from app.joblogic.base.schemas import HealthResponse
from app.joblogic.base.service import BaseService

router = APIRouter(tags=["base"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    """Report application status without contacting Joblogic."""

    return BaseService(request.app.state.settings).health()
