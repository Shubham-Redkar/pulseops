from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.dependencies import get_db


@pytest.mark.asyncio
async def test_get_db() -> None:
    mock_session = MagicMock()

    session_context = MagicMock()
    session_context.__aenter__ = AsyncMock(return_value=mock_session)
    session_context.__aexit__ = AsyncMock(return_value=None)

    with patch(
        "app.db.dependencies.async_session_maker",
        return_value=session_context,
    ):
        generator = get_db()

        session = await anext(generator)

        assert session is mock_session

        await generator.aclose()

    session_context.__aenter__.assert_awaited_once()
    session_context.__aexit__.assert_awaited_once()
