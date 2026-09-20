from uuid import UUID

from fastapi import APIRouter, status

from ...schemas.service import (
    CreateServiceRequest,
    ServiceResponse,
    UpdateServiceRequest,
)
from ..dependencies import ServiceManagerDep

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
    service_data: CreateServiceRequest,
    service_manager: ServiceManagerDep,
) -> ServiceResponse:
    return await service_manager.create_service(service_data)


@router.get(
    "",
    response_model=list[ServiceResponse],
)
async def get_services(
    service_manager: ServiceManagerDep,
) -> list[ServiceResponse]:
    return await service_manager.get_services()


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def get_service(
    service_id: UUID,
    service_manager: ServiceManagerDep,
) -> ServiceResponse:
    return await service_manager.get_service(service_id)


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def update_service(
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
    service_id: UUID,
    service_manager: ServiceManagerDep,
) -> None:
    await service_manager.delete_service(service_id)
