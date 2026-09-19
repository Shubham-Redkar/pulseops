from datetime import UTC, datetime
from uuid import UUID, uuid4

from ..core.exceptions import ServiceNotFoundError
from ..schemas.service import CreateServiceRequest, ServiceResponse, UpdateServiceRequest

services: dict[UUID, ServiceResponse] = {}


class ServiceManager:
    async def create_service(self, service_data: CreateServiceRequest) -> ServiceResponse:
        now = datetime.now(UTC)

        service_id = uuid4()

        service = ServiceResponse(
            id=service_id, **service_data.model_dump(), created_at=now, updated_at=now
        )

        services[service_id] = service

        return service

    async def get_services(self) -> list[ServiceResponse]:
        return list(services.values())

    async def get_service(self, service_id: UUID) -> ServiceResponse:
        if (service := services.get(service_id)) is None:
            raise ServiceNotFoundError(f"Service with ID '{service_id}' not found.")

        return service

    async def update_service(
        self, service_id: UUID, service_data: UpdateServiceRequest
    ) -> ServiceResponse:
        if (service := services.get(service_id)) is None:
            raise ServiceNotFoundError(f"Service with ID '{service_id}' not found.")

        updates = service_data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(service, field, value)

        service.updated_at = datetime.now(UTC)

        return service

    async def delete_service(self, service_id: UUID) -> None:
        if service_id not in services:
            raise ServiceNotFoundError(f"Service with ID '{service_id}' not found.")

        services.pop(service_id)


service_manager = ServiceManager()
