from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, ServiceNotFoundError
from app.db.models.service import Service
from app.schemas.service import CreateServiceRequest, UpdateServiceRequest
from app.services.service_service import ServiceManager


def create_service_model(
    name: str = "payment-service",
    description: str = "Handles payment processing.",
    team_id: UUID | None = None,
) -> Service:
    now = datetime.now(UTC)

    if team_id is None:
        team_id = uuid4()

    return Service(
        id=uuid4(),
        name=name,
        description=description,
        team_id=team_id,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_service(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    team_id = uuid4()
    now = datetime.now(UTC)

    service = Service(
        id=uuid4(),
        name="payment-service",
        description="Handles payment processing.",
        team_id=team_id,
        created_at=now,
        updated_at=now,
    )

    mock_service_repository.create.return_value = service

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    result = await manager.create_service(
        CreateServiceRequest(
            name="payment-service",
            description="Handles payment processing.",
            team_id=team_id,
        )
    )

    assert result.id == service.id
    assert result.name == "payment-service"
    assert result.description == "Handles payment processing."
    assert result.team_id == team_id
    assert result.created_at == now
    assert result.updated_at == now

    mock_service_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_service_duplicate_name(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    original_error = Exception('duplicate key value violates unique constraint "ix_services_name"')

    mock_service_repository.create.side_effect = IntegrityError(
        statement="INSERT INTO services",
        params={},
        orig=original_error,
    )

    team_id = uuid4()

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    with pytest.raises(
        ConflictError,
        match="A service with this name already exists.",
    ):
        await manager.create_service(
            CreateServiceRequest(
                name="payment-service",
                description="Handles payment processing.",
                team_id=team_id,
            )
        )

    mock_service_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_service(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    service = create_service_model()

    mock_service_repository.get_by_id.return_value = service

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    result = await manager.get_service(service.id)

    assert result.id == service.id
    assert result.name == service.name
    assert result.description == service.description
    assert result.team_id == service.team_id
    assert result.created_at == service.created_at
    assert result.updated_at == service.updated_at

    mock_service_repository.get_by_id.assert_awaited_once_with(service.id)


@pytest.mark.asyncio
async def test_get_service_not_found(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    service_id = uuid4()

    mock_service_repository.get_by_id.return_value = None

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    with pytest.raises(
        ServiceNotFoundError,
        match=f"Service with ID '{service_id}' was not found.",
    ):
        await manager.get_service(service_id)

    mock_service_repository.get_by_id.assert_awaited_once_with(service_id)


@pytest.mark.asyncio
async def test_get_services(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    first_service = create_service_model(
        name="payment-service",
        description="Handles payments.",
    )

    second_service = create_service_model(
        name="user-service",
        description="Handles users.",
    )

    mock_service_repository.get_all.return_value = (
        [first_service, second_service],
        2,
    )

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    result = await manager.get_services(
        limit=20,
        offset=0,
    )

    assert result.items
    assert len(result.items) == 2
    assert result.total == 2
    assert result.limit == 20
    assert result.offset == 0

    assert result.items[0].id == first_service.id
    assert result.items[0].name == "payment-service"
    assert result.items[0].team_id == first_service.team_id

    assert result.items[1].id == second_service.id
    assert result.items[1].name == "user-service"
    assert result.items[1].team_id == second_service.team_id

    mock_service_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_get_services_empty(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    mock_service_repository.get_all.return_value = (
        [],
        0,
    )

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    result = await manager.get_services(
        limit=20,
        offset=0,
    )

    assert result.items == []
    assert result.total == 0
    assert result.limit == 20
    assert result.offset == 0

    mock_service_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_update_service(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    service = create_service_model()

    updated_service = Service(
        id=service.id,
        name="updated-payment-service",
        description="Updated payment service.",
        team_id=service.team_id,
        created_at=service.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_service_repository.update.return_value = updated_service

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    result = await manager.update_service(
        service.id,
        UpdateServiceRequest(
            name="updated-payment-service",
            description="Updated payment service.",
            team_id=service.team_id,
        ),
    )

    assert result.id == service.id
    assert result.name == "updated-payment-service"
    assert result.description == "Updated payment service."
    assert result.team_id == service.team_id
    assert result.created_at == service.created_at
    assert result.updated_at == updated_service.updated_at

    mock_service_repository.update.assert_awaited_once_with(
        service.id,
        {
            "name": "updated-payment-service",
            "description": "Updated payment service.",
            "team_id": service.team_id,
        },
    )


@pytest.mark.asyncio
async def test_update_service_only_provided_fields(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    service = create_service_model()

    updated_service = Service(
        id=service.id,
        name="updated-payment-service",
        description=service.description,
        team_id=service.team_id,
        created_at=service.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_service_repository.update.return_value = updated_service

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    result = await manager.update_service(
        service.id,
        UpdateServiceRequest(
            name="updated-payment-service",
        ),
    )

    assert result.id == service.id
    assert result.name == "updated-payment-service"
    assert result.description == service.description
    assert result.team_id == service.team_id

    mock_service_repository.update.assert_awaited_once_with(
        service.id,
        {
            "name": "updated-payment-service",
        },
    )


@pytest.mark.asyncio
async def test_update_service_not_found(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    service_id = uuid4()

    mock_service_repository.update.return_value = None

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    with pytest.raises(
        ServiceNotFoundError,
        match=f"Service with ID '{service_id}' was not found.",
    ):
        await manager.update_service(
            service_id,
            UpdateServiceRequest(
                name="updated-payment-service",
            ),
        )

    mock_service_repository.update.assert_awaited_once_with(
        service_id,
        {
            "name": "updated-payment-service",
        },
    )


@pytest.mark.asyncio
async def test_delete_service(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    service_id = uuid4()

    mock_service_repository.delete.return_value = True

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    result = await manager.delete_service(service_id)

    assert result is None

    mock_service_repository.delete.assert_awaited_once_with(service_id)


@pytest.mark.asyncio
async def test_delete_service_not_found(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    service_id = uuid4()

    mock_service_repository.delete.return_value = False

    manager = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    with pytest.raises(
        ServiceNotFoundError,
        match=f"Service with ID '{service_id}' was not found.",
    ):
        await manager.delete_service(service_id)

    mock_service_repository.delete.assert_awaited_once_with(service_id)


@pytest.mark.asyncio
async def test_create_service_unexpected_integrity_error(
    mock_session: MagicMock,
    mock_service_repository: MagicMock,
) -> None:
    from sqlalchemy.exc import IntegrityError

    original_error = Exception("some unexpected database constraint")

    mock_service_repository.create.side_effect = IntegrityError(
        statement="INSERT INTO services",
        params={},
        orig=original_error,
    )

    service = ServiceManager(
        session=mock_session,
        repository=mock_service_repository,
    )

    with pytest.raises(IntegrityError):
        await service.create_service(
            CreateServiceRequest(
                name="payment-service",
                description="Handles payments.",
                team_id=uuid4(),
            )
        )

    mock_service_repository.create.assert_awaited_once()
