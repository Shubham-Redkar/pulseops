from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import Request

from app.api.errors import app_exception_handler


@pytest.mark.asyncio
async def test_app_exception_handler() -> None:
    request = MagicMock(spec=Request)

    request.state.request_id = uuid4()

    response = await app_exception_handler(
        request,
        Exception("unexpected error"),
    )

    assert response.status_code == 500

    assert response.body is not None
