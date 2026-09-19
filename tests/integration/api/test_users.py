from typing import Any

from httpx import AsyncClient


async def create_user(async_client: AsyncClient) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/users",
        json={
            "username": "john",
            "email": "john@example.com",
            "password": "john123",
            "role": "admin",
        },
    )

    assert response.status_code == 201

    return response.json()


async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/users",
        json={
            "username": "john",
            "email": "john@example.com",
            "password": "john123",
            "role": "admin",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "john"
    assert data["email"] == "john@example.com"
    assert data["role"] == "admin"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_user(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/users",
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


async def test_get_user_by_id(async_client: AsyncClient):
    user = await create_user(async_client)

    user_id = user["id"]

    response = await async_client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["username"] == "john"
    assert data["email"] == "john@example.com"
    assert data["role"] == "admin"
    assert "created_at" in data
    assert "updated_at" in data


async def test_update_user(async_client: AsyncClient):
    user = await create_user(async_client)

    user_id = user["id"]

    response = await async_client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "username": "john",
            "email": "john@example.in",
            "role": "viewer",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["username"] == "john"
    assert data["email"] == "john@example.in"
    assert data["role"] == "viewer"
    assert "created_at" in data
    assert "updated_at" in data


async def test_delete_user(async_client: AsyncClient):
    user = await create_user(async_client)

    user_id = user["id"]

    response = await async_client.delete(f"/api/v1/users/{user_id}")

    assert response.status_code == 204

    get_response = await async_client.get(f"/api/v1/users/{user_id}")

    assert get_response.status_code == 404
