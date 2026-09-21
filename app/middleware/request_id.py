from uuid import UUID, uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Attach a unique request identifier to each request.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id_header = request.headers.get("X-Request-ID")

        try:
            request_id = UUID(request_id_header) if request_id_header else uuid4()

        except ValueError:
            request_id = uuid4()

        request.state.request_id = request_id

        response = await call_next(request)

        response.headers["X-Request-ID"] = str(request_id)

        return response
