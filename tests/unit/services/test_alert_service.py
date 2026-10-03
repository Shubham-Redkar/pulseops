from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import AlertNotFoundError
from app.db.models.alert import Alert
from app.schemas.alert import CreateAlertRequest
from app.schemas.enums import Environment, IncidentSeverity
from app.services.alert_service import AlertService


def create_mock_alert() -> Alert:
    return Alert(
        id=uuid4(),
        service_id=uuid4(),
        incident_id=None,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
        source="prometheus",
        metric="error_rate",
        value=Decimal("18.7"),
        threshold=Decimal("5.0"),
        timestamp=datetime.now(UTC),
        fingerprint="mock_fingerprint",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def create_alert_service(
    mock_session: MagicMock,
    alert_repo: MagicMock | None = None,
    incident_repo: MagicMock | None = None,
    idempotency_repo: MagicMock | None = None,
) -> AlertService:
    return AlertService(
        session=mock_session,
        alert_repository=alert_repo or MagicMock(),
        incident_repository=incident_repo or MagicMock(),
        idempotency_repository=idempotency_repo or MagicMock(),
    )


@pytest.mark.asyncio
async def test_create_alert_new(mock_session: MagicMock) -> None:
    mock_session.begin = MagicMock()
    mock_session.begin.return_value.__aenter__ = AsyncMock()
    mock_session.begin.return_value.__aexit__ = AsyncMock()

    mock_alert_repo = MagicMock()
    mock_alert_repo.get_by_fingerprint = AsyncMock(return_value=None)
    mock_alert = create_mock_alert()
    mock_alert_repo.create = AsyncMock(return_value=mock_alert)

    mock_idempotency_repo = MagicMock()
    mock_idempotency_repo.get_by_key = AsyncMock(return_value=None)
    mock_idempotency_repo.create = AsyncMock()

    mock_incident_repo = MagicMock()
    mock_incident_repo.get_open_by_service_and_environment = AsyncMock(return_value=None)
    mock_incident = MagicMock()
    mock_incident.id = uuid4()
    mock_incident_repo.create = AsyncMock(return_value=mock_incident)

    service = create_alert_service(
        mock_session,
        alert_repo=mock_alert_repo,
        incident_repo=mock_incident_repo,
        idempotency_repo=mock_idempotency_repo,
    )

    req = CreateAlertRequest(
        service_id=mock_alert.service_id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
        source="prometheus",
        metric="error_rate",
        value=Decimal("18.7"),
        threshold=Decimal("5.0"),
        timestamp=datetime.now(UTC),
    )

    res = await service.create_alert(req, "test-idemp-key-1")

    assert res.id == mock_alert.id
    mock_alert_repo.get_by_fingerprint.assert_awaited_once()
    mock_alert_repo.create.assert_awaited_once()
    mock_incident_repo.create.assert_awaited_once()
    mock_idempotency_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_alert_duplicate_fingerprint(mock_session: MagicMock) -> None:
    mock_session.begin = MagicMock()
    mock_session.begin.return_value.__aenter__ = AsyncMock()
    mock_session.begin.return_value.__aexit__ = AsyncMock()

    mock_alert_repo = MagicMock()
    mock_alert = create_mock_alert()
    mock_alert_repo.get_by_fingerprint = AsyncMock(return_value=mock_alert)
    mock_alert_repo.create = AsyncMock()

    mock_idempotency_repo = MagicMock()
    mock_idempotency_repo.get_by_key = AsyncMock(return_value=None)

    service = create_alert_service(
        mock_session,
        alert_repo=mock_alert_repo,
        idempotency_repo=mock_idempotency_repo,
    )

    req = CreateAlertRequest(
        service_id=mock_alert.service_id,
        environment=Environment.PRODUCTION,
        severity=IncidentSeverity.CRITICAL,
        source="prometheus",
        metric="error_rate",
        value=Decimal("18.7"),
        threshold=Decimal("5.0"),
        timestamp=datetime.now(UTC),
    )

    res = await service.create_alert(req, "test-idemp-key-2")

    assert res.id == mock_alert.id
    mock_alert_repo.get_by_fingerprint.assert_awaited_once()
    mock_alert_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_get_alert_success(mock_session: MagicMock) -> None:
    mock_repo = MagicMock()
    mock_alert = create_mock_alert()
    mock_repo.get_by_id = AsyncMock(return_value=mock_alert)

    service = create_alert_service(mock_session, alert_repo=mock_repo)

    res = await service.get_alert(mock_alert.id)

    assert res.id == mock_alert.id
    mock_repo.get_by_id.assert_awaited_once_with(mock_alert.id)


@pytest.mark.asyncio
async def test_get_alert_not_found(mock_session: MagicMock) -> None:
    mock_repo = MagicMock()
    mock_repo.get_by_id = AsyncMock(return_value=None)

    service = create_alert_service(mock_session, alert_repo=mock_repo)
    alert_id = uuid4()

    with pytest.raises(AlertNotFoundError):
        await service.get_alert(alert_id)

    mock_repo.get_by_id.assert_awaited_once_with(alert_id)


@pytest.mark.asyncio
async def test_get_incident_alerts(mock_session: MagicMock) -> None:
    mock_repo = MagicMock()
    mock_alert = create_mock_alert()
    mock_repo.list_by_incident = AsyncMock(return_value=[mock_alert])

    service = create_alert_service(mock_session, alert_repo=mock_repo)
    incident_id = uuid4()

    res = await service.get_incident_alerts(incident_id)

    assert len(res) == 1
    assert res[0].id == mock_alert.id
    mock_repo.list_by_incident.assert_awaited_once_with(incident_id)
