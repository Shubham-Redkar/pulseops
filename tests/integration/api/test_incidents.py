from typing import Any

from httpx import AsyncClient


async def create_incident(async_client: AsyncClient) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/incidents",
        json={
            "title": "Payment API error rate elevated",
            "description": "Error rate exceeded the production threshold.",
            "service": "payment-service",
            "environment": "production",
            "severity": "critical",
        },
    )

    assert response.status_code == 201

    return response.json()


async def test_create_incident(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/incidents",
        json={
            "title": "Payment API error rate elevated",
            "description": "Error rate exceeded the production threshold.",
            "service": "payment-service",
            "environment": "production",
            "severity": "critical",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Payment API error rate elevated"
    assert data["description"] == "Error rate exceeded the production threshold."
    assert data["service"] == "payment-service"
    assert data["environment"] == "production"
    assert data["severity"] == "critical"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_incident(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/incidents",
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


async def test_get_incident_by_id(async_client: AsyncClient):
    incident = await create_incident(async_client)

    incident_id = incident["id"]

    response = await async_client.get(f"/api/v1/incidents/{incident_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Payment API error rate elevated"
    assert data["description"] == "Error rate exceeded the production threshold."
    assert data["service"] == "payment-service"
    assert data["environment"] == "production"
    assert data["severity"] == "critical"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_update_incident(async_client: AsyncClient):
    incident = await create_incident(async_client)

    incident_id = incident["id"]

    response = await async_client.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "severity": "low",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Payment API error rate elevated"
    assert data["description"] == "Error rate exceeded the production threshold."
    assert data["service"] == "payment-service"
    assert data["environment"] == "production"
    assert data["severity"] == "low"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_delete_incident(async_client: AsyncClient):
    incident = await create_incident(async_client)

    incident_id = incident["id"]

    response = await async_client.delete(f"/api/v1/incidents/{incident_id}")

    assert response.status_code == 204

    get_response = await async_client.get(f"/api/v1/incidents/{incident_id}")

    assert get_response.status_code == 404
