from typing import cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import ServiceNotFoundError
from ..db.models.service import Service
from ..repositories.service_repository import ServiceRepository
from ..schemas.base import PaginatedResponse
from ..schemas.service import CreateServiceRequest, ServiceResponse, UpdateServiceRequest
from ..types.service import ServiceUpdateData


class ServiceManager:
    """
    Manage service business operations.
    """

    def __init__(self, session: AsyncSession, repository: ServiceRepository) -> None:
        self.session = session
        self.repository = repository

    async def create_service(self, service_data: CreateServiceRequest) -> ServiceResponse:
        service = Service(**service_data.model_dump())

        async with self.session.begin():
            service = await self.repository.create(service)

        return ServiceResponse.model_validate(service)

    async def get_service(self, service_id: UUID) -> ServiceResponse:
        if (service := await self.repository.get_by_id(service_id)) is None:
            raise ServiceNotFoundError(service_id)

        return ServiceResponse.model_validate(service)

    async def get_services(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[ServiceResponse]:
        services, total = await self.repository.get_all(
            limit=limit,
            offset=offset,
        )

        return PaginatedResponse(
            items=[ServiceResponse.model_validate(service) for service in services],
            limit=limit,
            offset=offset,
            total=total,
        )

    async def update_service(
        self, service_id: UUID, service_data: UpdateServiceRequest
    ) -> ServiceResponse:
        update_data = cast(ServiceUpdateData, service_data.model_dump(exclude_unset=True))

        async with self.session.begin():
            if (service := await self.repository.update(service_id, update_data)) is None:
                raise ServiceNotFoundError(service_id)

        return ServiceResponse.model_validate(service)

    async def delete_service(self, service_id: UUID) -> None:
        async with self.session.begin():
            deleted = await self.repository.delete(service_id)

            if not deleted:
                raise ServiceNotFoundError(service_id)
