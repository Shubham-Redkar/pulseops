import hashlib
from uuid import UUID

from ..schemas.enums import Environment


def generate_alert_fingerprint(
    *,
    service_id: UUID,
    environment: Environment,
    source: str,
    metric: str,
) -> str:
    """
    Generate a deterministic fingerprint for an alert.

    The fingerprint identifies the underlying alert condition,
    rather than a specific metric observation.
    """

    fingerprint_data = f"{service_id}|{environment.value}|{source}|{metric}"

    return hashlib.sha256(
        fingerprint_data.encode("utf-8"),
    ).hexdigest()
