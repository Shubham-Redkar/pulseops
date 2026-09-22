from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ServiceUnavailableError

from .session import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Provide a database session for a request."""
    async with async_session_maker() as session:
        yield session


async def check_database() -> None:
    """Check whether PostgreSQL is reachable."""
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
    except Exception as exc:
        raise ServiceUnavailableError("Database is not ready.") from exc
