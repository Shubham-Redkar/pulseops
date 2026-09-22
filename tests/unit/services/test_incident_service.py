from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import IncidentNotFoundError
from app.db.models.incident import Incident
from app.schemas.enums import Environment, IncidentSeverity
from app.schemas.incident import CreateIncidentRequest, UpdateIncidentRequest
from app.services.incident_service import IncidentService


def create_incident_model(
    title: str = "Payment API error rate elevated",
    description: str = "Error rate exceeded the production threshold.",
    service_id: UUID | None = None,
    environment: Environment = Environment.PRODUCTION,
    severity: IncidentSeverity = IncidentSeverity.CRITICAL,
) -> Incident:
    now = datetime.now(UTC)

    if service_id is None:
        service_id = uuid4()

    return Incident(
        id=uuid4(),
        title=title,
        description=description,
        service_id=service_id,
        environment=environment,
        severity=severity,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_incident(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    service_id = uuid4()
    now = datetime.now(UTC)

    incident = Incident(
        id=uuid4(),
        title="Payment API error rate elevated",
        description="Error rate exceeded the production threshold.",
        service_id=service_id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
        created_at=now,
        updated_at=now,
    )

    mock_incident_repository.create.return_value = incident

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    result = await service.create_incident(
        CreateIncidentRequest(
            title="Payment API error rate elevated",
            description="Error rate exceeded the production threshold.",
            service_id=service_id,
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.CRITICAL,
        )
    )

    assert result.id == incident.id
    assert result.title == incident.title
    assert result.description == incident.description
    assert result.service_id == service_id
    assert result.environment == Environment.PRODUCTION
    assert result.severity == IncidentSeverity.CRITICAL
    assert result.created_at == now
    assert result.updated_at == now

    mock_incident_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_incident(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    incident = create_incident_model()

    mock_incident_repository.get_by_id.return_value = incident

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    result = await service.get_incident(incident.id)

    assert result.id == incident.id
    assert result.title == incident.title
    assert result.description == incident.description
    assert result.service_id == incident.service_id
    assert result.environment == incident.environment
    assert result.severity == incident.severity
    assert result.created_at == incident.created_at
    assert result.updated_at == incident.updated_at

    mock_incident_repository.get_by_id.assert_awaited_once_with(
        incident.id,
    )


@pytest.mark.asyncio
async def test_get_incident_not_found(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    incident_id = uuid4()

    mock_incident_repository.get_by_id.return_value = None

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    with pytest.raises(
        IncidentNotFoundError,
        match=f"Incident with ID '{incident_id}' was not found.",
    ):
        await service.get_incident(incident_id)

    mock_incident_repository.get_by_id.assert_awaited_once_with(
        incident_id,
    )


@pytest.mark.asyncio
async def test_get_incidents(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    first_incident = create_incident_model(
        title="Payment API error rate elevated",
        description="Payment API error rate is above threshold.",
    )

    second_incident = create_incident_model(
        title="User API latency increased",
        description="User API latency is above threshold.",
    )

    mock_incident_repository.get_all.return_value = (
        [first_incident, second_incident],
        2,
    )

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    result = await service.get_incidents(
        limit=20,
        offset=0,
    )

    assert result.items
    assert len(result.items) == 2
    assert result.total == 2
    assert result.limit == 20
    assert result.offset == 0

    assert result.items[0].id == first_incident.id
    assert result.items[0].title == first_incident.title
    assert result.items[0].service_id == first_incident.service_id

    assert result.items[1].id == second_incident.id
    assert result.items[1].title == second_incident.title
    assert result.items[1].service_id == second_incident.service_id

    mock_incident_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_get_incidents_empty(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    mock_incident_repository.get_all.return_value = (
        [],
        0,
    )

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    result = await service.get_incidents(
        limit=20,
        offset=0,
    )

    assert result.items == []
    assert result.total == 0
    assert result.limit == 20
    assert result.offset == 0

    mock_incident_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_update_incident(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    incident = create_incident_model()

    updated_incident = Incident(
        id=incident.id,
        title="Updated Payment API incident",
        description="Updated incident description.",
        service_id=incident.service_id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
        created_at=incident.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_incident_repository.update.return_value = updated_incident

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    result = await service.update_incident(
        incident.id,
        UpdateIncidentRequest(
            title="Updated Payment API incident",
            description="Updated incident description.",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.CRITICAL,
        ),
    )

    assert result.id == incident.id
    assert result.title == "Updated Payment API incident"
    assert result.description == "Updated incident description."
    assert result.service_id == incident.service_id
    assert result.environment == Environment.PRODUCTION
    assert result.severity == IncidentSeverity.CRITICAL
    assert result.created_at == incident.created_at
    assert result.updated_at == updated_incident.updated_at

    mock_incident_repository.update.assert_awaited_once_with(
        incident.id,
        {
            "title": "Updated Payment API incident",
            "description": "Updated incident description.",
            "environment": Environment.PRODUCTION,
            "severity": IncidentSeverity.CRITICAL,
        },
    )


@pytest.mark.asyncio
async def test_update_incident_only_provided_fields(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    incident = create_incident_model()

    updated_incident = Incident(
        id=incident.id,
        title="Updated Payment API incident",
        description=incident.description,
        service_id=incident.service_id,
        environment=incident.environment,
        severity=incident.severity,
        created_at=incident.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_incident_repository.update.return_value = updated_incident

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    result = await service.update_incident(
        incident.id,
        UpdateIncidentRequest(
            title="Updated Payment API incident",
        ),
    )

    assert result.id == incident.id
    assert result.title == "Updated Payment API incident"
    assert result.description == incident.description
    assert result.service_id == incident.service_id
    assert result.environment == incident.environment
    assert result.severity == incident.severity

    mock_incident_repository.update.assert_awaited_once_with(
        incident.id,
        {
            "title": "Updated Payment API incident",
        },
    )


@pytest.mark.asyncio
async def test_update_incident_not_found(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    incident_id = uuid4()

    mock_incident_repository.update.return_value = None

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    with pytest.raises(
        IncidentNotFoundError,
        match=f"Incident with ID '{incident_id}' was not found.",
    ):
        await service.update_incident(
            incident_id,
            UpdateIncidentRequest(
                title="Updated Payment API incident",
            ),
        )

    mock_incident_repository.update.assert_awaited_once_with(
        incident_id,
        {
            "title": "Updated Payment API incident",
        },
    )


@pytest.mark.asyncio
async def test_delete_incident(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    incident_id = uuid4()

    mock_incident_repository.delete.return_value = True

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    result = await service.delete_incident(incident_id)

    assert result is None

    mock_incident_repository.delete.assert_awaited_once_with(
        incident_id,
    )


@pytest.mark.asyncio
async def test_delete_incident_not_found(
    mock_session: MagicMock,
    mock_incident_repository: MagicMock,
) -> None:
    incident_id = uuid4()

    mock_incident_repository.delete.return_value = False

    service = IncidentService(
        session=mock_session,
        repository=mock_incident_repository,
    )

    with pytest.raises(
        IncidentNotFoundError,
        match=f"Incident with ID '{incident_id}' was not found.",
    ):
        await service.delete_incident(incident_id)

    mock_incident_repository.delete.assert_awaited_once_with(
        incident_id,
    )
