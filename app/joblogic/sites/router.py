from fastapi import APIRouter, Request

from app.joblogic.sites.schemas import (
    SiteCreate,
    SiteListResponse,
    SiteResponse,
    SiteSearchRequest,
)
from app.joblogic.sites.service import SiteService


router = APIRouter(
    prefix="/sites",
    tags=["sites"],
)


@router.post(
    "/search",
    response_model=SiteListResponse,
)
async def search_sites(
    payload: SiteSearchRequest,
    request: Request,
) -> SiteListResponse:

    service = SiteService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )

    result = await service.get_all_sites(
        payload.model_dump(by_alias=True)
    )

    return SiteListResponse.model_validate(result)


@router.post(
    "",
    response_model=SiteResponse,
)
async def create_site(
    payload: SiteCreate,
    request: Request,
) -> SiteResponse:

    service = SiteService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )

    result = await service.create_site(
        payload.model_dump(by_alias=True)
    )

    return SiteResponse.model_validate(result)