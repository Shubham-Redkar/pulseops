from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Incident, Service, Team
from app.repositories.incident_repository import IncidentRepository
from app.schemas.enums import Environment, IncidentSeverity


async def create_service(
    test_session: AsyncSession,
) -> Service:
    team = Team(
        name=f"Payments Team {uuid4()}",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.flush()

    service = Service(
        name=f"payment-service-{uuid4()}",
        description="Handles payment processing and transaction management.",
        team_id=team.id,
    )

    test_session.add(service)
    await test_session.flush()

    return service


@pytest.mark.asyncio
async def test_create_incident(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    incident = Incident(
        title="Payment API error rate elevated",
        description="Error rate exceeded the production threshold.",
        service_id=service.id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    result = await incident_repository.create(incident)
    await test_session.commit()

    assert result.id is not None
    assert result.title == "Payment API error rate elevated"
    assert result.description == "Error rate exceeded the production threshold."
    assert result.service_id == service.id
    assert result.environment == Environment.PRODUCTION
    assert result.severity == IncidentSeverity.CRITICAL


@pytest.mark.asyncio
async def test_get_by_id(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    incident = Incident(
        title="Payment API error rate elevated",
        description="Error rate exceeded the production threshold.",
        service_id=service.id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    await incident_repository.create(incident)
    await test_session.commit()

    result = await incident_repository.get_by_id(incident.id)

    assert result is not None
    assert result.id == incident.id
    assert result.title == "Payment API error rate elevated"
    assert result.service_id == service.id


@pytest.mark.asyncio
async def test_get_all(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    first_incident = Incident(
        title="Payment incident",
        description="Payment errors increased.",
        service_id=service.id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    second_incident = Incident(
        title="Order incident",
        description="Order processing errors increased.",
        service_id=service.id,
        environment=Environment.STAGING,
        severity=IncidentSeverity.HIGH,
    )

    await incident_repository.create(first_incident)
    await incident_repository.create(second_incident)
    await test_session.commit()

    incidents, total = await incident_repository.get_all(
        limit=20,
        offset=0,
    )

    assert len(incidents) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_get_all_pagination(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    for title in [
        "Incident A",
        "Incident B",
        "Incident C",
    ]:
        await incident_repository.create(
            Incident(
                title=title,
                description=f"{title} description.",
                service_id=service.id,
                environment=Environment.PRODUCTION,
                severity=IncidentSeverity.HIGH,
            )
        )

    await test_session.commit()

    incidents, total = await incident_repository.get_all(
        limit=2,
        offset=0,
    )

    assert len(incidents) == 2
    assert total == 3


@pytest.mark.asyncio
async def test_update_incident(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    incident = Incident(
        title="Payment incident",
        description="Payment errors increased.",
        service_id=service.id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    await incident_repository.create(incident)
    await test_session.commit()

    result = await incident_repository.update(
        incident.id,
        {
            "title": "Updated Payment Incident",
            "description": "Updated description.",
            "severity": IncidentSeverity.HIGH,
        },
    )

    await test_session.commit()

    assert result is not None
    assert result.id == incident.id
    assert result.title == "Updated Payment Incident"
    assert result.description == "Updated description."
    assert result.severity == IncidentSeverity.HIGH
    assert result.service_id == service.id


@pytest.mark.asyncio
async def test_update_incident_multiple_fields(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    incident = Incident(
        title="Payment incident",
        description="Payment errors increased.",
        service_id=service.id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    await incident_repository.create(incident)
    await test_session.commit()

    result = await incident_repository.update(
        incident.id,
        {
            "title": "Updated Incident",
            "environment": Environment.STAGING,
            "severity": IncidentSeverity.LOW,
        },
    )

    await test_session.commit()

    assert result is not None
    assert result.id == incident.id
    assert result.title == "Updated Incident"
    assert result.environment == Environment.STAGING
    assert result.severity == IncidentSeverity.LOW


@pytest.mark.asyncio
async def test_update_incident_not_found(
    incident_repository: IncidentRepository,
):
    result = await incident_repository.update(
        uuid4(),
        {
            "title": "Does Not Exist",
        },
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_incident_empty_values(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    incident = Incident(
        title="Payment incident",
        description="Payment errors increased.",
        service_id=service.id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    await incident_repository.create(incident)
    await test_session.commit()

    result = await incident_repository.update(
        incident.id,
        {},
    )

    assert result is not None
    assert result.id == incident.id
    assert result.title == "Payment incident"
    assert result.description == "Payment errors increased."


@pytest.mark.asyncio
async def test_delete_incident(
    test_session: AsyncSession,
    incident_repository: IncidentRepository,
):
    service = await create_service(test_session)

    incident = Incident(
        title="Payment API error rate elevated",
        description="Error rate exceeded the production threshold.",
        service_id=service.id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    await incident_repository.create(incident)
    await test_session.commit()

    result = await incident_repository.delete(incident.id)

    await test_session.commit()

    assert result is True

    deleted_incident = await incident_repository.get_by_id(incident.id)

    assert deleted_incident is None


@pytest.mark.asyncio
async def test_delete_incident_not_found(
    incident_repository: IncidentRepository,
):
    result = await incident_repository.delete(uuid4())

    assert result is False
