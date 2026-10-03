import uuid
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.alert import Alert
from app.db.models.incident import Incident
from app.db.models.service import Service
from app.db.models.team import Team
from app.repositories.alert_repository import AlertRepository
from app.schemas.enums import Environment, IncidentSeverity


async def create_mock_service(
    session: AsyncSession,
) -> Service:
    team = Team(
        id=uuid.uuid4(),
        name=f"Team {uuid.uuid4()}",
    )
    session.add(team)
    await session.flush()

    service = Service(
        id=uuid.uuid4(),
        name=f"Service {uuid.uuid4()}",
        description="Test",
        team_id=team.id,
    )
    session.add(service)
    await session.flush()
    return service


async def create_mock_incident(
    session: AsyncSession,
    service_id: uuid.UUID,
) -> Incident:
    incident = Incident(
        id=uuid.uuid4(),
        title="Test Incident",
        description="A test incident",
        service_id=service_id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )
    session.add(incident)
    await session.flush()
    return incident


def create_mock_alert(
    service_id: uuid.UUID,
    incident_id: uuid.UUID | None = None,
) -> Alert:
    return Alert(
        id=uuid.uuid4(),
        service_id=service_id,
        incident_id=incident_id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
        source="prometheus",
        metric="error_rate",
        value=Decimal("18.7"),
        threshold=Decimal("5.0"),
        timestamp=datetime.now(UTC),
        fingerprint=f"mock_fingerprint_{uuid.uuid4()}",
    )


@pytest.mark.asyncio
async def test_create_alert(
    test_session: AsyncSession,
) -> None:
    service = await create_mock_service(test_session)
    alert = create_mock_alert(service.id)

    repo = AlertRepository(test_session)
    saved_alert = await repo.create(alert)

    assert saved_alert.id == alert.id
    assert saved_alert.fingerprint == alert.fingerprint


@pytest.mark.asyncio
async def test_get_by_id(
    test_session: AsyncSession,
) -> None:
    service = await create_mock_service(test_session)
    alert = create_mock_alert(service.id)

    repo = AlertRepository(test_session)
    await repo.create(alert)

    found_alert = await repo.get_by_id(alert.id)

    assert found_alert is not None
    assert found_alert.id == alert.id


@pytest.mark.asyncio
async def test_get_by_fingerprint(
    test_session: AsyncSession,
) -> None:
    service = await create_mock_service(test_session)
    alert = create_mock_alert(service.id)

    repo = AlertRepository(test_session)
    await repo.create(alert)

    found_alert = await repo.get_by_fingerprint(alert.fingerprint)

    assert found_alert is not None
    assert found_alert.fingerprint == alert.fingerprint


@pytest.mark.asyncio
async def test_list_by_incident(
    test_session: AsyncSession,
) -> None:
    service = await create_mock_service(test_session)
    incident = await create_mock_incident(test_session, service.id)
    alert1 = create_mock_alert(service.id, incident_id=incident.id)
    alert2 = create_mock_alert(service.id, incident_id=incident.id)

    repo = AlertRepository(test_session)
    await repo.create(alert1)
    await repo.create(alert2)

    alerts = await repo.list_by_incident(incident.id)

    assert len(alerts) == 2
    alert_ids = [a.id for a in alerts]
    assert alert1.id in alert_ids
    assert alert2.id in alert_ids
