from typing import Any

from httpx import AsyncClient

TEAM_ID = "66dee2d6-f869-4152-9fb9-8461c73506ce"


async def create_service(async_client: AsyncClient) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/services",
        json={
            "name": "payment-service",
            "description": "Handles payment processing and transaction management.",
            "team_id": TEAM_ID,
        },
    )

    assert response.status_code == 201

    return response.json()


async def test_create_service(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/services",
        json={
            "name": "payment-service",
            "description": "Handles payment processing and transaction management.",
            "team_id": TEAM_ID,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "payment-service"
    assert data["description"] == ("Handles payment processing and transaction management.")
    assert data["team_id"] == TEAM_ID
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_services(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/services",
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


async def test_get_service_by_id(async_client: AsyncClient):
    service = await create_service(async_client)

    service_id = service["id"]

    response = await async_client.get(f"/api/v1/services/{service_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == service_id
    assert data["name"] == "payment-service"
    assert data["description"] == ("Handles payment processing and transaction management.")
    assert data["team_id"] == TEAM_ID
    assert "created_at" in data
    assert "updated_at" in data


async def test_update_service(async_client: AsyncClient):
    service = await create_service(async_client)

    service_id = service["id"]

    response = await async_client.patch(
        f"/api/v1/services/{service_id}",
        json={
            "name": "updated-payment-service",
            "description": "Updated payment processing service.",
            "team_id": TEAM_ID,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == service_id
    assert data["name"] == "updated-payment-service"
    assert data["description"] == "Updated payment processing service."
    assert data["team_id"] == TEAM_ID
    assert "created_at" in data
    assert "updated_at" in data


async def test_delete_service(async_client: AsyncClient):
    service = await create_service(async_client)

    service_id = service["id"]

    response = await async_client.delete(f"/api/v1/services/{service_id}")

    assert response.status_code == 204

    get_response = await async_client.get(f"/api/v1/services/{service_id}")

    assert get_response.status_code == 404
