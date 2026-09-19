from collections.abc import Generator
from uuid import uuid4

import pytest

from app.core.exceptions import IncidentNotFoundError
from app.schemas.enums import Environment, IncidentSeverity
from app.schemas.incident import (
    CreateIncidentRequest,
    UpdateIncidentRequest,
)
from app.services.incident_service import IncidentService, incidents


@pytest.fixture
def incident_service() -> Generator[IncidentService]:
    incidents.clear()

    service = IncidentService()

    yield service

    incidents.clear()


@pytest.mark.asyncio
async def test_create_incident(incident_service: IncidentService):
    incident_data = CreateIncidentRequest(
        title="Payment API error rate elevated",
        description="Error rate exceeded the production threshold.",
        service="payment-service",
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
    )

    result = await incident_service.create_incident(incident_data)

    assert result.id is not None
    assert result.title == "Payment API error rate elevated"
    assert result.description == "Error rate exceeded the production threshold."
    assert result.service == "payment-service"
    assert result.environment == Environment.PRODUCTION
    assert result.severity == IncidentSeverity.CRITICAL
    assert result.created_at is not None
    assert result.updated_at is not None
    assert result.created_at == result.updated_at
    assert result.id in incidents
    assert incidents[result.id] == result


@pytest.mark.asyncio
async def test_get_incidents_empty(incident_service: IncidentService):
    result = await incident_service.get_incidents()

    assert result == []


@pytest.mark.asyncio
async def test_get_incidents(incident_service: IncidentService):
    first_incident = await incident_service.create_incident(
        CreateIncidentRequest(
            title="Payment API error rate elevated",
            description="Error rate exceeded the production threshold.",
            service="payment-service",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.CRITICAL,
        )
    )

    second_incident = await incident_service.create_incident(
        CreateIncidentRequest(
            title="User API latency elevated",
            description="Response latency exceeded the normal threshold.",
            service="user-service",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.HIGH,
        )
    )

    result = await incident_service.get_incidents()

    assert len(result) == 2
    assert first_incident in result
    assert second_incident in result


@pytest.mark.asyncio
async def test_get_incident(incident_service: IncidentService):
    created_incident = await incident_service.create_incident(
        CreateIncidentRequest(
            title="Payment API error rate elevated",
            description="Error rate exceeded the production threshold.",
            service="payment-service",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.CRITICAL,
        )
    )

    result = await incident_service.get_incident(created_incident.id)

    assert result == created_incident
    assert result.id == created_incident.id


@pytest.mark.asyncio
async def test_get_incident_not_found(incident_service: IncidentService):
    incident_id = uuid4()

    with pytest.raises(
        IncidentNotFoundError,
        match=f"Incident with ID '{incident_id}' was not found.",
    ):
        await incident_service.get_incident(incident_id)


@pytest.mark.asyncio
async def test_update_incident(incident_service: IncidentService):
    created_incident = await incident_service.create_incident(
        CreateIncidentRequest(
            title="Payment API error rate elevated",
            description="Error rate exceeded the production threshold.",
            service="payment-service",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.CRITICAL,
        )
    )

    original_created_at = created_incident.created_at

    updated_incident = await incident_service.update_incident(
        created_incident.id,
        UpdateIncidentRequest(
            title="Payment API recovered",
            description="Error rate returned to normal.",
            service="payment-service",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.LOW,
        ),
    )

    assert updated_incident.id == created_incident.id
    assert updated_incident.title == "Payment API recovered"
    assert updated_incident.description == "Error rate returned to normal."
    assert updated_incident.service == "payment-service"
    assert updated_incident.environment == Environment.PRODUCTION
    assert updated_incident.severity == IncidentSeverity.LOW
    assert updated_incident.created_at == original_created_at
    assert updated_incident.updated_at is not None


@pytest.mark.asyncio
async def test_update_incident_only_updates_provided_fields(
    incident_service: IncidentService,
):
    created_incident = await incident_service.create_incident(
        CreateIncidentRequest(
            title="Payment API error rate elevated",
            description="Error rate exceeded the production threshold.",
            service="payment-service",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.CRITICAL,
        )
    )

    original_description = created_incident.description
    original_service = created_incident.service
    original_environment = created_incident.environment
    original_severity = created_incident.severity
    original_created_at = created_incident.created_at

    updated_incident = await incident_service.update_incident(
        created_incident.id,
        UpdateIncidentRequest(
            title="Updated payment incident",
        ),
    )

    assert updated_incident.title == "Updated payment incident"
    assert updated_incident.description == original_description
    assert updated_incident.service == original_service
    assert updated_incident.environment == original_environment
    assert updated_incident.severity == original_severity
    assert updated_incident.created_at == original_created_at
    assert updated_incident.updated_at is not None


@pytest.mark.asyncio
async def test_update_incident_not_found(
    incident_service: IncidentService,
):
    incident_id = uuid4()

    with pytest.raises(
        IncidentNotFoundError,
        match=f"Incident with ID '{incident_id}' was not found.",
    ):
        await incident_service.update_incident(
            incident_id,
            UpdateIncidentRequest(
                title="Updated payment incident",
            ),
        )


@pytest.mark.asyncio
async def test_delete_incident(incident_service: IncidentService):
    created_incident = await incident_service.create_incident(
        CreateIncidentRequest(
            title="Payment API error rate elevated",
            description="Error rate exceeded the production threshold.",
            service="payment-service",
            environment=Environment.PRODUCTION,
            severity=IncidentSeverity.CRITICAL,
        )
    )

    assert created_incident.id in incidents

    result = await incident_service.delete_incident(created_incident.id)

    assert result is None
    assert created_incident.id not in incidents


@pytest.mark.asyncio
async def test_delete_incident_not_found(
    incident_service: IncidentService,
):
    incident_id = uuid4()

    with pytest.raises(
        IncidentNotFoundError,
        match=f"Incident with ID '{incident_id}' was not found.",
    ):
        await incident_service.delete_incident(incident_id)
