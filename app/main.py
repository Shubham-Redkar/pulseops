from fastapi import FastAPI

from .api.errors import app_exception_handler, conflict_handler, not_found_handler
from .api.routes.router import api_router
from .core.exceptions import AppException, ConflictError, NotFoundError
from .middleware.request_id import RequestIDMiddleware

app = FastAPI(
    title="PulseOps API",
    version="1.0.0",
    description="API for managing production incidents and service reliability.",
)

app.add_middleware(RequestIDMiddleware)

app.add_exception_handler(
    ConflictError,
    conflict_handler,
)

app.add_exception_handler(NotFoundError, not_found_handler)

app.add_exception_handler(AppException, app_exception_handler)


@app.get("/", tags=["Root"])
async def home() -> dict[str, str]:
    return {
        "service": "PulseOps API",
        "message": "API is live and ready to serve requests",
        "status": "operational",
    }


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/health/live", tags=["Health"])
async def liveness() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness() -> dict[str, str]:
    # check PostgreSQL
    # check Redis

    return {"status": "ready"}


app.include_router(api_router, prefix="/api/v1")
