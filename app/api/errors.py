from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..core.errors import ErrorCode
from ..core.exceptions import AppException, ConflictError, NotFoundError, ServiceUnavailableError
from ..schemas.errors import ErrorResponse


def create_error_response(
    *,
    status_code: int,
    code: ErrorCode,
    message: str,
    request: Request,
) -> JSONResponse:
    """Create a standardized JSON error response."""
    request_id = request.state.request_id

    error = ErrorResponse(
        code=code,
        message=message,
        request_id=request_id,
    )

    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(mode="json"),
    )


async def not_found_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle resource-not-found exceptions."""
    app_exc = exc if isinstance(exc, AppException) else None

    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code=ErrorCode.NOT_FOUND,
        message=app_exc.message if app_exc else "Resource was not found.",
        request=request,
    )


async def conflict_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle resource-conflict exceptions."""
    app_exc = exc if isinstance(exc, AppException) else None

    return create_error_response(
        status_code=status.HTTP_409_CONFLICT,
        code=ErrorCode.CONFLICT,
        message=str(app_exc) if app_exc else "The request conflicts with existing state.",
        request=request,
    )


async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unexpected application exceptions."""
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected application error occurred.",
        request=request,
    )


async def service_unavailable_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return create_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code=ErrorCode.SERVICE_UNAVAILABLE,
        message=str(exc),
        request=request,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register application exception handlers."""

    app.add_exception_handler(
        ConflictError,
        conflict_handler,
    )

    app.add_exception_handler(
        NotFoundError,
        not_found_handler,
    )

    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )

    app.add_exception_handler(
        ServiceUnavailableError,
        service_unavailable_handler,
    )
