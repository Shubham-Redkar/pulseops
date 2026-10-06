from collections.abc import Mapping

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from ..core.errors import ErrorCode
from ..core.exceptions import (
    AppException,
    ConflictError,
    ForbiddenError,
    InvalidTokenError,
    NotFoundError,
    RateLimitExceededError,
    ServiceUnavailableError,
    UnauthorizedError,
)
from ..schemas.errors import ErrorResponse

ExceptionMapping = tuple[int, ErrorCode]


EXCEPTION_MAPPING: Mapping[
    type[AppException],
    ExceptionMapping,
] = {
    NotFoundError: (
        status.HTTP_404_NOT_FOUND,
        ErrorCode.NOT_FOUND,
    ),
    ConflictError: (
        status.HTTP_409_CONFLICT,
        ErrorCode.CONFLICT,
    ),
    ServiceUnavailableError: (
        status.HTTP_503_SERVICE_UNAVAILABLE,
        ErrorCode.SERVICE_UNAVAILABLE,
    ),
    UnauthorizedError: (
        status.HTTP_401_UNAUTHORIZED,
        ErrorCode.UNAUTHORIZED,
    ),
    InvalidTokenError: (
        status.HTTP_401_UNAUTHORIZED,
        ErrorCode.UNAUTHORIZED,
    ),
    ForbiddenError: (
        status.HTTP_403_FORBIDDEN,
        ErrorCode.FORBIDDEN,
    ),
    RateLimitExceededError: (
        status.HTTP_429_TOO_MANY_REQUESTS,
        ErrorCode.RATE_LIMIT_EXCEEDED,
    ),
}


def create_error_response(
    *,
    request: Request,
    status_code: int,
    code: ErrorCode,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """
    Create a standardized API error response.
    """
    error = ErrorResponse(
        code=code,
        message=message,
        request_id=request.state.request_id,
    )

    return JSONResponse(
        status_code=status_code,
        content=error.model_dump(mode="json"),
        headers=headers,
    )


def get_exception_mapping(
    exc: AppException,
) -> ExceptionMapping:
    """
    Resolve the HTTP status code and API error code for an
    application exception.
    """
    for exception_type, mapping in EXCEPTION_MAPPING.items():
        if isinstance(exc, exception_type):
            return mapping

    return (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        ErrorCode.INTERNAL,
    )


async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle expected application exceptions.
    """
    if not isinstance(exc, AppException):
        return await unhandled_exception_handler(
            request,
            exc,
        )

    status_code, error_code = get_exception_mapping(exc)

    headers: dict[str, str] | None = None

    if isinstance(exc, RateLimitExceededError):
        headers = {
            "X-RateLimit-Limit": str(exc.limit),
            "X-RateLimit-Remaining": str(exc.remaining),
            "X-RateLimit-Reset": str(exc.reset),
            "Retry-After": str(exc.reset),
        }

    response = create_error_response(
        request=request,
        status_code=status_code,
        code=error_code,
        message=exc.message,
        headers=headers,
    )

    if isinstance(exc, RateLimitExceededError):
        response.headers["X-RateLimit-Limit"] = str(exc.limit)
        response.headers["X-RateLimit-Remaining"] = str(exc.remaining)
        response.headers["X-RateLimit-Reset"] = str(exc.reset)

    return response


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected application/runtime exceptions.
    """
    return create_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL,
        message="An unexpected internal error occurred.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register application-wide exception handlers.
    """
    app.add_exception_handler(
        AppException,
        app_exception_handler,
    )

    app.add_exception_handler(
        Exception,
        unhandled_exception_handler,
    )
