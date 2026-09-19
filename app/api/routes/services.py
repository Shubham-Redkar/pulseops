from uuid import UUID

from fastapi import APIRouter, status

from ...schemas.service import (
    CreateServiceRequest,
    ServiceResponse,
    UpdateServiceRequest,
)
from ...services.service_service import service_manager

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
) -> ServiceResponse:
    return await service_manager.create_service(service_data)


@router.get(
    "",
    response_model=list[ServiceResponse],
)
async def get_services() -> list[ServiceResponse]:
    return await service_manager.get_services()


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def get_service(
    service_id: UUID,
) -> ServiceResponse:
    return await service_manager.get_service(service_id)


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
)
async def update_service(
    service_id: UUID,
    service_data: UpdateServiceRequest,
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
) -> None:
    await service_manager.delete_service(service_id)
