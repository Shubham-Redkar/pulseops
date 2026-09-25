from uuid import UUID

from fastapi import APIRouter, Query, status

from ...schemas.base import PaginatedResponse
from ...schemas.service import (
    CreateServiceRequest,
    ServiceResponse,
    UpdateServiceRequest,
)
from ..dependencies import CurrentUserDep, ServiceManagerDep

router = APIRouter(
    prefix="/services",
    tags=["Services"],
)


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_service(
    current_user: CurrentUserDep,
    service_data: CreateServiceRequest,
    service_manager: ServiceManagerDep,
) -> ServiceResponse:
    return await service_manager.create_service(service_data)


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def get_service(
    current_user: CurrentUserDep,
    service_id: UUID,
    service_manager: ServiceManagerDep,
) -> ServiceResponse:
    return await service_manager.get_service(service_id)


@router.get(
    "",
    response_model=PaginatedResponse[ServiceResponse],
)
async def get_services(
    current_user: CurrentUserDep,
    service_manager: ServiceManagerDep,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of services to return.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of services to skip.",
    ),
) -> PaginatedResponse[ServiceResponse]:
    return await service_manager.get_services(
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def update_service(
    current_user: CurrentUserDep,
    service_id: UUID,
    service_data: UpdateServiceRequest,
    service_manager: ServiceManagerDep,
) -> ServiceResponse:
    return await service_manager.update_service(
        service_id,
        service_data,
    )


@router.delete(
    "/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service(
    current_user: CurrentUserDep,
    service_id: UUID,
    service_manager: ServiceManagerDep,
) -> None:
    await service_manager.delete_service(service_id)
