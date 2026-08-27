from fastapi import APIRouter, Request

from app.joblogic.staff.schemas import (
    StaffSearchRequest,
    StaffListResponse,
    StaffDetailsResponse,
)
from app.joblogic.staff.service import StaffService

router = APIRouter(
    prefix="/staff",
    tags=["staff"],
)


@router.post("/search", response_model=StaffListResponse)
async def get_all_staff(
    payload: StaffSearchRequest,
    request: Request,
) -> StaffListResponse:
    service = StaffService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )
    result = await service.get_all_staff(
        payload.model_dump(by_alias=True)
    )
    return StaffListResponse.model_validate(result)


@router.get("/{unique_id}", response_model=StaffDetailsResponse)
async def get_staff_by_unique_id(
    unique_id: str,
    tenant_id: str,
    request: Request,
) -> StaffDetailsResponse:
    service = StaffService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )
    result = await service.get_staff_by_unique_id(
        unique_id=unique_id,
        tenant_id=tenant_id,
    )
    return StaffDetailsResponse.model_validate(result)
