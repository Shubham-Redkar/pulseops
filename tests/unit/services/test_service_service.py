from collections.abc import Generator
from uuid import uuid4

import pytest

from app.core.exceptions import ServiceNotFoundError
from app.schemas.service import CreateServiceRequest, UpdateServiceRequest
from app.services.service_service import ServiceManager, services

TEAM_ID = uuid4()


@pytest.fixture
def service_manager() -> Generator[ServiceManager]:
    services.clear()

    manager = ServiceManager()

    yield manager

    services.clear()


@pytest.mark.asyncio
async def test_create_service(service_manager: ServiceManager):
    service_data = CreateServiceRequest(
        name="payment-service",
        description="Handles payment processing.",
        team_id=TEAM_ID,
    )

    result = await service_manager.create_service(service_data)

    assert result.id is not None
    assert result.name == "payment-service"
    assert result.description == "Handles payment processing."
    assert result.team_id == TEAM_ID
    assert result.created_at is not None
    assert result.updated_at is not None
    assert result.created_at == result.updated_at
    assert result.id in services
    assert services[result.id] == result


@pytest.mark.asyncio
async def test_get_services_empty(service_manager: ServiceManager):
    result = await service_manager.get_services()

    assert result == []


@pytest.mark.asyncio
async def test_get_services(service_manager: ServiceManager):
    first_service = await service_manager.create_service(
        CreateServiceRequest(
            name="payment-service",
            description="Handles payments.",
            team_id=TEAM_ID,
        )
    )

    second_service = await service_manager.create_service(
        CreateServiceRequest(
            name="user-service",
            description="Handles users.",
            team_id=TEAM_ID,
        )
    )

    result = await service_manager.get_services()

    assert len(result) == 2
    assert first_service in result
    assert second_service in result


@pytest.mark.asyncio
async def test_get_service(service_manager: ServiceManager):
    created_service = await service_manager.create_service(
        CreateServiceRequest(
            name="payment-service",
            description="Handles payments.",
            team_id=TEAM_ID,
        )
    )

    result = await service_manager.get_service(created_service.id)

    assert result == created_service
    assert result.id == created_service.id


@pytest.mark.asyncio
async def test_service_not_found(service_manager: ServiceManager):
    service_id = uuid4()

    with pytest.raises(ServiceNotFoundError, match=f"Service with ID '{service_id}' not found."):
        await service_manager.get_service(service_id)


@pytest.mark.asyncio
async def test_update_service(service_manager: ServiceManager):
    created_service = await service_manager.create_service(
        CreateServiceRequest(
            name="payment-service",
            description="Handles payments.",
            team_id=TEAM_ID,
        )
    )

    original_created_at = created_service.created_at

    updated_service = await service_manager.update_service(
        created_service.id,
        UpdateServiceRequest(
            name="updated-payment-service",
            description="Updated payment processing service.",
            team_id=TEAM_ID,
        ),
    )

    assert updated_service.id == created_service.id
    assert updated_service.name == "updated-payment-service"
    assert updated_service.description == "Updated payment processing service."
    assert updated_service.team_id == TEAM_ID
    assert updated_service.created_at == original_created_at
    assert updated_service.updated_at is not None


@pytest.mark.asyncio
async def test_update_service_only_updates_provided_fields(
    service_manager: ServiceManager,
):
    created_service = await service_manager.create_service(
        CreateServiceRequest(
            name="payment-service",
            description="Handles payments.",
            team_id=TEAM_ID,
        )
    )

    original_description = created_service.description
    original_team_id = created_service.team_id
    original_created_at = created_service.created_at
    updated_service = await service_manager.update_service(
        created_service.id,
        UpdateServiceRequest(
            name="updated-payment-service",
        ),
    )

    assert updated_service.name == "updated-payment-service"
    assert updated_service.description == original_description
    assert updated_service.team_id == original_team_id
    assert updated_service.created_at == original_created_at
    assert updated_service.updated_at is not None


@pytest.mark.asyncio
async def test_update_service_not_found(service_manager: ServiceManager):
    service_id = uuid4()

    with pytest.raises(
        ServiceNotFoundError,
        match=f"Service with ID '{service_id}' not found.",
    ):
        await service_manager.update_service(
            service_id, UpdateServiceRequest(name="updated-payment-service")
        )


@pytest.mark.asyncio
async def test_delete_service(service_manager: ServiceManager):
    created_service = await service_manager.create_service(
        CreateServiceRequest(
            name="payment-service",
            description="Handles payments.",
            team_id=TEAM_ID,
        )
    )

    assert created_service.id in services

    result = await service_manager.delete_service(created_service.id)

    assert result is None
    assert created_service.id not in services


@pytest.mark.asyncio
async def test_delete_service_not_found(service_manager: ServiceManager):
    service_id = uuid4()

    with pytest.raises(ServiceNotFoundError, match=f"Service with ID '{service_id}' not found."):
        await service_manager.delete_service(service_id)
