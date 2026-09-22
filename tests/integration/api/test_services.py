from typing import Any
from uuid import UUID, uuid4

from httpx import AsyncClient


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


async def test_create_service(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    response = await async_client.post(
        "/api/v1/services",
        json={
            "name": "payment-service",
            "description": "Handles payment processing and transaction management.",
            "team_id": str(team_id),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "payment-service"
    assert data["description"] == ("Handles payment processing and transaction management.")
    assert data["team_id"] == str(team_id)
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_services(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    await create_service(
        async_client,
        team_id,
        name="payment-service",
    )

    await create_service(
        async_client,
        team_id,
        name="order-service",
        description="Handles order processing.",
    )

    response = await async_client.get(
        "/api/v1/services?limit=1&offset=0",
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


async def test_get_service_by_id(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    response = await async_client.get(
        f"/api/v1/services/{service_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(service_id)
    assert data["name"] == service["name"]
    assert data["description"] == service["description"]
    assert data["team_id"] == str(team_id)
    assert "created_at" in data
    assert "updated_at" in data


async def test_update_service(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    response = await async_client.patch(
        f"/api/v1/services/{service_id}",
        json={
            "name": "updated-payment-service",
            "description": "Updated payment processing service.",
            "team_id": str(team_id),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(service_id)
    assert data["name"] == "updated-payment-service"
    assert data["description"] == "Updated payment processing service."
    assert data["team_id"] == str(team_id)
    assert "created_at" in data
    assert "updated_at" in data


async def test_delete_service(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    service = await create_service(async_client, team_id)
    service_id = UUID(service["id"])

    response = await async_client.delete(
        f"/api/v1/services/{service_id}",
    )

    assert response.status_code == 204

    get_response = await async_client.get(
        f"/api/v1/services/{service_id}",
    )

    assert get_response.status_code == 404


async def test_get_service_not_found(async_client: AsyncClient):
    service_id = uuid4()

    response = await async_client.get(
        f"/api/v1/services/{service_id}",
    )

    assert response.status_code == 404


async def test_update_service_not_found(async_client: AsyncClient):
    service_id = uuid4()

    response = await async_client.patch(
        f"/api/v1/services/{service_id}",
        json={
            "name": "updated-payment-service",
        },
    )

    assert response.status_code == 404


async def test_delete_service_not_found(async_client: AsyncClient):
    service_id = uuid4()

    response = await async_client.delete(
        f"/api/v1/services/{service_id}",
    )

    assert response.status_code == 404


async def test_create_duplicate_service(async_client: AsyncClient):
    team = await create_team(async_client)
    team_id = UUID(team["id"])

    await create_service(
        async_client,
        team_id,
        name="payment-service",
    )

    response = await async_client.post(
        "/api/v1/services",
        json={
            "name": "payment-service",
            "description": "Another description.",
            "team_id": str(team_id),
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["code"] == "CONFLICT"
    assert data["message"] == "A service with this name already exists."
