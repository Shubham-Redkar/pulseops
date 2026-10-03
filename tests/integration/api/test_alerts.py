import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.service import Service
from app.db.models.team import Team


async def create_mock_service_for_api(session: AsyncSession) -> Service:
    team = Team(id=uuid.uuid4(), name=f"Team {uuid.uuid4()}")
    session.add(team)
    await session.flush()

    service = Service(
        id=uuid.uuid4(),
        name=f"Service {uuid.uuid4()}",
        description="Test",
        team_id=team.id,
    )
    session.add(service)
    await session.commit()
    return service


@pytest.mark.asyncio
async def test_create_alert_api(
    auth_client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    service = await create_mock_service_for_api(test_session)

    payload = {
        "service_id": str(service.id),
        "environment": "production",
        "severity": "critical",
        "source": "prometheus",
        "metric": "error_rate",
        "value": 18.7,
        "threshold": 5.0,
        "timestamp": "2026-09-29T10:00:00Z",
    }

    response = await auth_client.post(
        "/api/v1/alerts",
        json=payload,
        headers={
            "Idempotency-Key": f"test-key-{uuid.uuid4()}",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["service_id"] == str(service.id)
    assert data["metric"] == "error_rate"


@pytest.mark.asyncio
async def test_get_alert_api(
    auth_client: AsyncClient,
    test_session: AsyncSession,
) -> None:
    service = await create_mock_service_for_api(test_session)

    payload = {
        "service_id": str(service.id),
        "environment": "production",
        "severity": "critical",
        "source": "prometheus",
        "metric": "cpu_usage",
        "value": 99.9,
        "threshold": 80.0,
        "timestamp": "2026-09-29T10:00:00Z",
    }

    create_response = await auth_client.post(
        "/api/v1/alerts",
        json=payload,
        headers={
            "Idempotency-Key": f"test-key-{uuid.uuid4()}",
        },
    )
    assert create_response.status_code == 201
    alert_id = create_response.json()["id"]

    get_response = await auth_client.get(f"/api/v1/alerts/{alert_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == alert_id


@pytest.mark.asyncio
async def test_get_alert_not_found_api(
    auth_client: AsyncClient,
) -> None:
    fake_id = str(uuid.uuid4())
    get_response = await auth_client.get(f"/api/v1/alerts/{fake_id}")
    assert get_response.status_code == 404
