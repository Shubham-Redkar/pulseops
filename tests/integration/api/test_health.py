from httpx import AsyncClient


async def test_home(async_client: AsyncClient):
    response = await async_client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "PulseOps API",
        "message": "API is live and ready to serve requests",
        "status": "operational",
    }


async def test_health(async_client: AsyncClient):
    response = await async_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


async def test_liveness(async_client: AsyncClient):
    response = await async_client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


async def test_readiness(async_client: AsyncClient):
    response = await async_client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
