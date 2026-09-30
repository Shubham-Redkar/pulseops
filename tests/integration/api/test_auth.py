from typing import Any

from httpx import AsyncClient


async def register_user(
    async_client: AsyncClient,
    first_name: str = "Test",
    last_name: str = "User",
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "Password123!",
) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    from sqlalchemy import text

    from tests.conftest import engine

    async with engine.begin() as connection:
        await connection.execute(
            text(
                f"UPDATE users SET email_verified = true, role = 'admin' "
                f"WHERE username = '{username}'"
            )
        )

    return response.json()


async def login_user(
    async_client: AsyncClient,
    username: str = "testuser",
    password: str = "Password123!",
) -> dict[str, Any]:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()


async def test_register(async_client: AsyncClient):
    data = await register_user(async_client)

    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "viewer"
    assert data["team_id"] is None

    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert "password" not in data
    assert "password_hash" not in data


async def test_register_duplicate_username(async_client: AsyncClient):
    await register_user(async_client)

    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Another",
            "last_name": "User",
            "username": "testuser",
            "email": "another@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 409


async def test_register_duplicate_email(async_client: AsyncClient):
    await register_user(async_client)

    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Another",
            "last_name": "User",
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == 409


async def test_login(async_client: AsyncClient):
    await register_user(async_client)

    data = await login_user(async_client)

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

    assert "refresh_token" in data
    assert "refresh_expires_in" in data


async def test_login_invalid_password(async_client: AsyncClient):
    await register_user(async_client)

    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


async def test_login_user_not_found(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": "does-not-exist",
            "password": "Password123!",
        },
    )

    assert response.status_code == 401


async def test_get_me(auth_client: AsyncClient):
    response = await auth_client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "first_name" in data
    assert "last_name" in data
    assert "username" in data
    assert "email" in data
    assert "role" in data
    assert "team_id" in data
    assert "created_at" in data
    assert "updated_at" in data

    assert data["username"] == "test_user"
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "Test"
    assert data["last_name"] == "User"


async def test_get_me_unauthorized(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 401


async def test_refresh_token(async_client: AsyncClient):
    await register_user(async_client)

    login_data = await login_user(async_client)

    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": login_data["refresh_token"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

    assert "refresh_token" in data
    assert "refresh_expires_in" in data

    assert data["refresh_token"] != login_data["refresh_token"]


async def test_refresh_token_cannot_be_reused(
    async_client: AsyncClient,
):
    await register_user(async_client)

    login_data = await login_user(async_client)

    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": login_data["refresh_token"],
        },
    )

    assert response.status_code == 200

    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": login_data["refresh_token"],
        },
    )

    assert response.status_code == 401


async def test_refresh_token_invalid(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": "invalid-refresh-token",
        },
    )

    assert response.status_code == 401


async def test_logout(async_client: AsyncClient):
    await register_user(async_client)

    login_data = await login_user(async_client)

    response = await async_client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": login_data["refresh_token"],
        },
    )

    assert response.status_code == 204


async def test_logout_revokes_refresh_token(async_client: AsyncClient):
    await register_user(async_client)

    login_data = await login_user(async_client)
    refresh_token = login_data["refresh_token"]

    response = await async_client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 204

    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 401


async def test_logout_invalid_refresh_token(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/auth/logout",
        json={
            "refresh_token": "invalid-refresh-token",
        },
    )

    assert response.status_code == 401
