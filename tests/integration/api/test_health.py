from unittest.mock import AsyncMock, patch

from httpx import AsyncClient

from app.core.exceptions import ServiceUnavailableError


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
    with patch(
        "app.main.check_database",
        new_callable=AsyncMock,
    ) as mock_check_database:
        response = await async_client.get("/health/ready")

    mock_check_database.assert_awaited_once()

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


async def test_readiness_when_database_unavailable(
    async_client: AsyncClient,
):
    with patch(
        "app.main.check_database",
        new_callable=AsyncMock,
        side_effect=ServiceUnavailableError("Database is not ready."),
    ):
        response = await async_client.get("/health/ready")

    assert response.status_code == 503
