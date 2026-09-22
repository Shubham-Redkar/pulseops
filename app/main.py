from fastapi import FastAPI

from .api.errors import register_exception_handlers
from .api.routes.router import api_router
from .db.dependencies import check_database
from .middleware.request_id import RequestIDMiddleware

app = FastAPI(
    title="PulseOps API",
    version="1.0.0",
    description="API for managing production incidents and service reliability.",
)

app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)


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
    await check_database()

    return {"status": "ready"}


app.include_router(api_router, prefix="/api/v1")
