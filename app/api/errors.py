from fastapi import Request, status
from fastapi.responses import JSONResponse

from ..schemas.enums import ErrorCode
from ..schemas.errors import ErrorResponse


def create_error_response(
    *, status_code: int, code: ErrorCode, message: str, request: Request
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)

    error = ErrorResponse(code=code, message=message, request_id=request_id)

    return JSONResponse(status_code=status_code, content=error.model_dump(mode="json"))


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code=ErrorCode.NOT_FOUND,
        message=str(exc) or "Resource not found.",
        request=request,
    )


async def conflict_handler(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response(
        status_code=status.HTTP_409_CONFLICT,
        code=ErrorCode.CONFLICT,
        message=str(exc) or "The request conflicts with existing state.",
        request=request,
    )


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected application error occurred.",
        request=request,
    )
