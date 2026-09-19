from typing import Any

from httpx import AsyncClient


async def create_team(async_client: AsyncClient) -> dict[str, Any]:
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

    assert data["name"] == "Payments Team"
    assert data["description"] == (
        "Owns payment processing services and ensures reliable payment operations."
    )
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_team(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/teams",
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


async def test_get_team_by_id(async_client: AsyncClient):
    team = await create_team(async_client)

    team_id = team["id"]

    response = await async_client.get(f"/api/v1/teams/{team_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == team_id
    assert data["name"] == "Payments Team"
    assert (
        data["description"]
        == "Owns payment processing services and ensures reliable payment operations."
    )
    assert "created_at" in data
    assert "updated_at" in data


async def test_update_team(async_client: AsyncClient):
    team = await create_team(async_client)

    team_id = team["id"]

    response = await async_client.patch(
        f"/api/v1/teams/{team_id}",
        json={
            "name": "Updated Payment Team",
            "description": (
                "Updated - Owns payment processing services and ensures"
                " reliable payment operations."
            ),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == team_id
    assert data["name"] == "Updated Payment Team"
    assert (
        data["description"]
        == "Updated - Owns payment processing services and ensures reliable payment operations."
    )
    assert "created_at" in data
    assert "updated_at" in data


async def test_delete_team(async_client: AsyncClient):
    team = await create_team(async_client)

    team_id = team["id"]

    response = await async_client.delete(f"/api/v1/teams/{team_id}")

    assert response.status_code == 204

    get_response = await async_client.get(f"/api/v1/teams/{team_id}")

    assert get_response.status_code == 404
