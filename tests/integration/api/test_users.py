from typing import Any
from uuid import uuid4

from httpx import AsyncClient

from app.schemas.enums import UserRole


async def create_user(
    async_client: AsyncClient,
    username: str = "john",
    email: str = "john@example.com",
    password: str = "john123456",
    role: UserRole = UserRole.ADMIN,
) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/users",
        json={"username": username, "email": email, "password": password, "role": role.value},
    )

    assert response.status_code == 201

    return response.json()


async def test_create_user(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/users",
        json={
            "username": "john",
            "email": "john@example.com",
            "password": "john123456",
            "role": "admin",
        },
    )
    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "john"
    assert data["email"] == "john@example.com"
    assert data["role"] == "admin"
    assert "password" not in data
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_user_by_id(async_client: AsyncClient):
    user = await create_user(async_client)

    user_id = user["id"]

    response = await async_client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["username"] == user["username"]
    assert data["email"] == user["email"]
    assert data["role"] == user["role"]
    assert "created_at" in data
    assert "updated_at" in data


async def test_get_users(async_client: AsyncClient):
    await create_user(
        async_client,
        username="john",
        email="john@example.com",
    )

    await create_user(
        async_client,
        username="jane",
        email="jane@example.com",
    )

    response = await async_client.get(
        "/api/v1/users?limit=1&offset=0",
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


async def test_get_user_not_found(async_client: AsyncClient):
    user_id = uuid4()

    response = await async_client.get(
        f"/api/v1/users/{user_id}",
    )

    assert response.status_code == 404


async def test_update_user_not_found(async_client: AsyncClient):
    user_id = uuid4()

    response = await async_client.patch(
        f"/api/v1/users/{user_id}",
        json={
            "username": "Updated user",
        },
    )

    assert response.status_code == 404


async def test_delete_user_not_found(async_client: AsyncClient):
    user_id = uuid4()

    response = await async_client.delete(
        f"/api/v1/users/{user_id}",
    )

    assert response.status_code == 404


async def test_create_duplicate_username(async_client: AsyncClient):
    await create_user(
        async_client,
        username="john",
        email="john@example.com",
    )

    response = await async_client.post(
        "/api/v1/users",
        json={
            "username": "john",
            "email": "john2@example.in",
            "password": "john123456",
            "role": "admin",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["code"] == "CONFLICT"
    assert data["message"] == "A user with this username already exists."


async def test_create_duplicate_email(async_client: AsyncClient):
    await create_user(
        async_client,
        username="john",
        email="john@example.com",
    )

    response = await async_client.post(
        "/api/v1/users",
        json={
            "username": "john2",
            "email": "john@example.com",
            "password": "john123456",
            "role": "admin",
        },
    )

    assert response.status_code == 409

    data = response.json()

    assert data["code"] == "CONFLICT"
    assert data["message"] == "A user with this email already exists."
