from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from .session import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession]:
    """Provide a database session for a request."""
    async with async_session_maker() as session:
        yield session
