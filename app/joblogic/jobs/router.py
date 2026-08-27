from fastapi import APIRouter, Request

from app.joblogic.jobs.schemas import (
    JobCreate,
    JobResponse,
    JobSearchRequest,
    JobTypeSearchRequest,
    JobCategorySearchRequest,
    PrioritySearchRequest,
    TradeSearchRequest,
)
from app.joblogic.jobs.service import JobService


router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


def get_service(request: Request) -> JobService:
    return JobService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )


# ============================================================
# CREATE JOB
# ============================================================

@router.post(
    "",
    response_model=JobResponse,
)
async def create_job(
    payload: JobCreate,
    request: Request,
) -> JobResponse:

    service = get_service(request)

    result = await service.create_job(
        payload.model_dump(by_alias=True, exclude_none=True)
    )

    return JobResponse.model_validate(result)


# ============================================================
# SEARCH JOBS
# ============================================================

@router.post(
    "/search",
)
async def search_jobs(
    payload: JobSearchRequest,
    request: Request,
):

    service = get_service(request)

    return await service.search_jobs(
        payload.model_dump(by_alias=True)
    )


# ============================================================
# SEARCH JOB TYPES
# ============================================================

@router.post(
    "/types/search",
)
async def search_job_types(
    payload: JobTypeSearchRequest,
    request: Request,
):

    service = get_service(request)

    return await service.search_job_types(
        payload.model_dump(by_alias=True)
    )


# ============================================================
# SEARCH JOB CATEGORIES
# ============================================================

@router.post(
    "/categories/search",
)
async def search_job_categories(
    payload: JobCategorySearchRequest,
    request: Request,
):

    service = get_service(request)

    return await service.search_job_categories(
        payload.model_dump(by_alias=True)
    )


# ============================================================
# SEARCH PRIORITIES
# ============================================================

@router.post(
    "/priorities/search",
)
async def search_priorities(
    payload: PrioritySearchRequest,
    request: Request,
):

    service = get_service(request)

    return await service.search_priorities(
        payload.model_dump(by_alias=True)
    )


# ============================================================
# SEARCH TRADES
# ============================================================

@router.post(
    "/trades/search",
)
async def search_trades(
    payload: TradeSearchRequest,
    request: Request,
):

    service = get_service(request)

    return await service.search_trades(
        payload.model_dump(by_alias=True)
    )
