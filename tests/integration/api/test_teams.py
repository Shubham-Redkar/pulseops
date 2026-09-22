from typing import Any
from uuid import UUID, uuid4

from httpx import AsyncClient


async def create_team(
    async_client: AsyncClient,
    name: str = "Payments Team",
    description: str = (
        "Owns payment processing services and ensures reliable payment operations."
    ),
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


async def test_create_team(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/teams",
        json={
            "name": "Payments Team",
            "description": (
                "Owns payment processing services and ensures reliable payment operations."
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "id" in data
    assert data["id"] is not None
    assert data["name"] == "Payments Team"
    assert data["description"] == (
        "Owns payment processing services and ensures reliable payment operations."
    )
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_teams(async_client: AsyncClient):
    await create_team(
        async_client,
        name="Payments Team",
        description="Owns payment processing services.",
    )

    await create_team(
        async_client,
        name="Orders Team",
        description="Owns order processing services.",
    )

    response = await async_client.get(
        "/api/v1/teams?limit=1&offset=0",
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


async def test_get_team_by_id(async_client: AsyncClient):
    team = await create_team(async_client)

    team_id = UUID(team["id"])

    response = await async_client.get(
        f"/api/v1/teams/{team_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(team_id)
    assert data["name"] == team["name"]
    assert data["description"] == team["description"]
    assert "created_at" in data
    assert "updated_at" in data


async def test_update_team(async_client: AsyncClient):
    team = await create_team(async_client)

    team_id = UUID(team["id"])

    response = await async_client.patch(
        f"/api/v1/teams/{team_id}",
        json={
            "name": "Updated Payment Team",
            "description": (
                "Updated - Owns payment processing services and ensures "
                "reliable payment operations."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(team_id)
    assert data["name"] == "Updated Payment Team"
    assert data["description"] == (
        "Updated - Owns payment processing services and ensures reliable payment operations."
    )
    assert "created_at" in data
    assert "updated_at" in data


async def test_delete_team(async_client: AsyncClient):
    team = await create_team(async_client)

    team_id = UUID(team["id"])

    response = await async_client.delete(
        f"/api/v1/teams/{team_id}",
    )

    assert response.status_code == 204

    get_response = await async_client.get(
        f"/api/v1/teams/{team_id}",
    )

    assert get_response.status_code == 404


async def test_get_team_not_found(async_client: AsyncClient):
    team_id = uuid4()

    response = await async_client.get(
        f"/api/v1/teams/{team_id}",
    )

    assert response.status_code == 404


async def test_update_team_not_found(async_client: AsyncClient):
    team_id = uuid4()

    response = await async_client.patch(
        f"/api/v1/teams/{team_id}",
        json={
            "name": "Updated Team",
        },
    )

    assert response.status_code == 404


async def test_delete_team_not_found(async_client: AsyncClient):
    team_id = uuid4()

    response = await async_client.delete(
        f"/api/v1/teams/{team_id}",
    )

    assert response.status_code == 404


async def test_create_duplicate_team(async_client: AsyncClient):
    await create_team(
        async_client,
        name="Payments Team",
    )

    response = await async_client.post(
        "/api/v1/teams",
        json={
            "name": "Payments Team",
            "description": "Another description.",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["code"] == "CONFLICT"
    assert data["message"] == "A team with this name already exists."
