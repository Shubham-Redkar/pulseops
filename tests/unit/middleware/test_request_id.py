from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Request
from starlette.responses import Response

from app.middleware.request_id import RequestIDMiddleware


@pytest.mark.asyncio
async def test_request_id_invalid_header_generates_new_id() -> None:
    middleware = RequestIDMiddleware(MagicMock())

    request = MagicMock(spec=Request)
    request.headers = {
        "X-Request-ID": "not-a-valid-uuid",
    }
    request.state = MagicMock()

    response = Response(status_code=200)

    call_next = AsyncMock(return_value=response)

    result = await middleware.dispatch(request, call_next)

    assert result.status_code == 200
    assert request.state.request_id is not None
    assert result.headers["X-Request-ID"] == str(request.state.request_id)

    call_next.assert_awaited_once_with(request)
