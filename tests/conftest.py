from collections.abc import AsyncGenerator
from typing import Literal

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.db.dependencies import get_db
from app.main import app


class TestSettings(BaseSettings):
    database_url: str

    secret_key: SecretStr = Field(min_length=32)

    jwt_algorithm: Literal["HS256", "HS384", "HS512"]

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = TestSettings()  # type: ignore

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    poolclass=NullPool,
)

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
async def test_session() -> AsyncGenerator[AsyncSession]:
    """
    Provide a database session for repository-level tests.
    """
    async with async_session_maker() as session:
        yield session


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncGenerator[None]:
    """
    Reset the test database before every test.
    """
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                TRUNCATE TABLE
                    incidents,
                    services,
                    users,
                    teams,
                    alerts,
                    idempotency_keys
                CASCADE
                """
            )
        )

    yield


@pytest.fixture
async def async_client(
    reset_database: None,
) -> AsyncGenerator[AsyncClient]:
    """
    Provide an unauthenticated HTTP client.

    A fresh database session is created for every HTTP request.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_client() -> AsyncGenerator[AsyncClient]:
    """
    Provide an authenticated HTTP client.

    Authentication setup and every subsequent API request use
    independent database sessions.
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        register_response = await client.post(
            "/api/v1/auth/register",
            json={
                "first_name": "Test",
                "last_name": "User",
                "username": "test_user",
                "email": "test@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert register_response.status_code == 201

        from sqlalchemy import text

        async with engine.begin() as connection:
            await connection.execute(
                text(
                    "UPDATE users SET email_verified = true, role = 'admin' "
                    "WHERE username = 'test_user'"
                )
            )

        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "test_user",
                "password": "StrongPassword123!",
            },
        )

        assert login_response.status_code == 200

        access_token = login_response.json()["access_token"]

        client.headers["Authorization"] = f"Bearer {access_token}"

        yield client

    app.dependency_overrides.clear()
