from fastapi import FastAPI

from .api.routes.router import api_router

app = FastAPI(
    title="PulseOps API",
    version="1.0.0",
    description="API for managing production incidents and service reliability.",
)


@app.get("/", tags=["Root"])
async def home():
    return {
        "service": "PulseOps API",
        "message": "API is live and ready to serve requests",
        "status": "operational",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


@app.get("/health/live", tags=["Health"])
async def liveness():
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def readiness():
    # check PostgreSQL
    # check Redis

    return {"status": "ready"}


app.include_router(api_router, prefix="/api/v1")
