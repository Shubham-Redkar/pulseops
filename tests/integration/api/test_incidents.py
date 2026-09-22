from typing import Any
from uuid import UUID, uuid4

from httpx import AsyncClient

from app.schemas.enums import Environment, IncidentSeverity


async def create_team(
    async_client: AsyncClient,
    name: str = "Payments Team",
    description: str = "Owns payment processing services.",
) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/teams",
        json={
            "name": name,
            "description": description,
        },
    )

    assert response.status_code == 201

    return response.json()


async def create_service(
    async_client: AsyncClient,
    team_id: UUID,
    name: str = "payment-service",
    description: str = "Handles payment processing and transaction management.",
) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/services",
        json={
            "name": name,
            "description": description,
            "team_id": str(team_id),
        },
    )

    assert response.status_code == 201

    return response.json()


async def create_incident(
    async_client: AsyncClient,
    service_id: UUID,
    title: str = "Payment API error rate elevated",
    description: str = "Error rate exceeded the production threshold.",
    environment: Environment = Environment.PRODUCTION,
    severity: IncidentSeverity = IncidentSeverity.CRITICAL,
) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/incidents",
        json={
            "title": title,
            "description": description,
            "service_id": str(service_id),
            "environment": environment.value,
            "severity": severity.value,
        },
    )

    assert response.status_code == 201

    return response.json()


async def test_create_incident(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    response = await async_client.post(
        "/api/v1/incidents",
        json={
            "title": "Payment API error rate elevated",
            "description": "Error rate exceeded the production threshold.",
            "service_id": str(service_id),
            "environment": "production",
            "severity": "critical",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Payment API error rate elevated"
    assert data["description"] == "Error rate exceeded the production threshold."
    assert data["service_id"] == str(service_id)
    assert data["environment"] == "production"
    assert data["severity"] == "critical"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_incident_by_id(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    incident = await create_incident(async_client, service_id)
    incident_id = UUID(incident["id"])

    response = await async_client.get(
        f"/api/v1/incidents/{incident_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(incident_id)
    assert data["title"] == incident["title"]
    assert data["description"] == incident["description"]
    assert data["service_id"] == str(service_id)
    assert data["environment"] == incident["environment"]
    assert data["severity"] == incident["severity"]
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_incidents(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    await create_incident(
        async_client,
        service_id,
        title="Payment incident",
    )

    await create_incident(
        async_client,
        service_id,
        title="Order incident",
        severity=IncidentSeverity.HIGH,
    )

    response = await async_client.get(
        "/api/v1/incidents?limit=1&offset=0",
    )

    assert response.status_code == 200

    data: dict[str, Any] = response.json()

    assert isinstance(data, dict)

    assert "items" in data
    assert "limit" in data
    assert "offset" in data
    assert "total" in data

    assert data["limit"] == 1
    assert data["offset"] == 0
    assert data["total"] == 2
    assert len(data["items"]) == 1


async def test_update_incident(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    incident = await create_incident(async_client, service_id)
    incident_id = UUID(incident["id"])

    response = await async_client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "severity": "low",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(incident_id)
    assert data["title"] == incident["title"]
    assert data["description"] == incident["description"]
    assert data["service_id"] == str(service_id)
    assert data["environment"] == incident["environment"]
    assert data["severity"] == "low"
    assert "created_at" in data
    assert "updated_at" in data


async def test_delete_incident(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    incident = await create_incident(async_client, service_id)
    incident_id = UUID(incident["id"])

    response = await async_client.delete(
        f"/api/v1/incidents/{incident_id}",
    )

    assert response.status_code == 204

    get_response = await async_client.get(
        f"/api/v1/incidents/{incident_id}",
    )

    assert get_response.status_code == 404


async def test_get_incident_not_found(async_client: AsyncClient):
    incident_id = uuid4()

    response = await async_client.get(
        f"/api/v1/incidents/{incident_id}",
    )

    assert response.status_code == 404


async def test_update_incident_not_found(async_client: AsyncClient):
    incident_id = uuid4()

    response = await async_client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "title": "Payment incident",
        },
    )

    assert response.status_code == 404


async def test_delete_incident_not_found(async_client: AsyncClient):
    incident_id = uuid4()

    response = await async_client.delete(
        f"/api/v1/incidents/{incident_id}",
    )

    assert response.status_code == 404
