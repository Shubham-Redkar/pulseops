from uuid import UUID

from app.core.fingerprinting import generate_alert_fingerprint
from app.schemas.enums import Environment

SERVICE_ID = UUID("66dee2d6-f869-4152-9fb9-8461c73506ce")


def test_same_alert_condition_produces_same_fingerprint() -> None:
    fingerprint_1 = generate_alert_fingerprint(
        service_id=SERVICE_ID,
        environment=Environment.PRODUCTION,
        source="prometheus",
        metric="error_rate",
    )

    fingerprint_2 = generate_alert_fingerprint(
        service_id=SERVICE_ID,
        environment=Environment.PRODUCTION,
        source="prometheus",
        metric="error_rate",
    )

    assert fingerprint_1 == fingerprint_2


def test_different_metric_produces_different_fingerprint() -> None:
    fingerprint_1 = generate_alert_fingerprint(
        service_id=SERVICE_ID,
        environment=Environment.PRODUCTION,
        source="prometheus",
        metric="error_rate",
    )

    fingerprint_2 = generate_alert_fingerprint(
        service_id=SERVICE_ID,
        environment=Environment.PRODUCTION,
        source="prometheus",
        metric="latency",
    )

    assert fingerprint_1 != fingerprint_2


def test_different_environment_produces_different_fingerprint() -> None:
    fingerprint_1 = generate_alert_fingerprint(
        service_id=SERVICE_ID,
        environment=Environment.PRODUCTION,
        source="prometheus",
        metric="error_rate",
    )

    fingerprint_2 = generate_alert_fingerprint(
        service_id=SERVICE_ID,
        environment=Environment.STAGING,
        source="prometheus",
        metric="error_rate",
    )

    assert fingerprint_1 != fingerprint_2
