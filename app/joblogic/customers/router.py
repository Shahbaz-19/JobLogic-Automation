from fastapi import APIRouter, Request 

from app.joblogic.customers.schemas import (
    CustomerCreate,
    CustomerResponse,
    CustomerSearchRequest,
    CustomerListResponse,
    CustomerDetailsResponse,
)
from app.joblogic.customers.service import CustomerService


router = APIRouter(
    prefix="/customers",
    tags=["customers"],
)


@router.post("", response_model=CustomerResponse)
async def create_customer(
    payload: CustomerCreate,
    request: Request,
) -> CustomerResponse:

    service = CustomerService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )

    result = await service.create_customer(
        payload.model_dump(by_alias=True)
    )

    return CustomerResponse.model_validate(result)


@router.post("/search", response_model=CustomerListResponse)
async def search_customers(
    payload: CustomerSearchRequest,
    request: Request,
) -> CustomerListResponse:

    service = CustomerService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )

    result = await service.get_all_customers(
        payload.model_dump(by_alias=True)
    )

    return CustomerListResponse.model_validate(result)


@router.get(
    "/{customer_id}",
    response_model=CustomerDetailsResponse,
)
async def get_customer(
    customer_id: int,
    request: Request,
    tenant_id: str,
    include_additional_details: bool = False,
) -> CustomerDetailsResponse:

    service = CustomerService(
        request.app.state.settings,
        request.app.state.joblogic_client,
    )

    result = await service.get_customer_by_id(
        customer_id=customer_id,
        include_additional_details=include_additional_details,
        tenant_id=tenant_id,
    )

    return CustomerDetailsResponse.model_validate(result)
