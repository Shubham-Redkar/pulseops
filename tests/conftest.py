from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.db.dependencies import get_db
from app.main import app


class TestSettings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = TestSettings()  # type: ignore

engine = create_async_engine(
    settings.database_url, echo=False, pool_pre_ping=True, poolclass=NullPool
)

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
async def test_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


@pytest.fixture
async def async_client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncGenerator[None]:
    async with engine.begin() as connection:
        await connection.execute(
            text(
                """
                TRUNCATE TABLE
                    incidents,
                    services,
                    users,
                    teams
                CASCADE
                """
            )
        )

    yield
