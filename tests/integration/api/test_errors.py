from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI, Request

from app.api.errors import (
    app_exception_handler,
    conflict_handler,
    not_found_handler,
    register_exception_handlers,
)
from app.core.exceptions import AppException, ConflictError, NotFoundError


@pytest.mark.asyncio
async def test_app_exception_handler() -> None:
    request = MagicMock(spec=Request)
    request.state.request_id = uuid4()

    response = await app_exception_handler(
        request,
        Exception("unexpected error"),
    )

    assert response.status_code == 500


def test_register_exception_handlers() -> None:
    app = FastAPI()

    register_exception_handlers(app)

    assert app.exception_handlers[ConflictError] is conflict_handler
    assert app.exception_handlers[NotFoundError] is not_found_handler
    assert app.exception_handlers[AppException] is app_exception_handler
