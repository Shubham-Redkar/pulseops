import secrets
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.exceptions import AlertNotFoundError, ConflictError, ServiceUnavailableError
from ..core.fingerprinting import generate_alert_fingerprint
from ..core.redis import RedisStore
from ..db.models import (
    Alert,
    IdempotencyKey,
    Incident,
)
from ..repositories import (
    AlertRepository,
    IdempotencyRepository,
    IncidentRepository,
)
from ..schemas.alert import AlertResponse, CreateAlertRequest


class AlertService:
    """
    Manage alert business operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        alert_repository: AlertRepository,
        incident_repository: IncidentRepository,
        idempotency_repository: IdempotencyRepository,
        redis_store: RedisStore,
    ) -> None:
        self.session = session
        self.alert_repository = alert_repository
        self.incident_repository = incident_repository
        self.idempotency_repository = idempotency_repository
        self.redis_store = redis_store

    async def create_alert(
        self,
        alert_data: CreateAlertRequest,
        idempotency_key: str,
    ) -> AlertResponse:
        fingerprint = generate_alert_fingerprint(
            service_id=alert_data.service_id,
            environment=alert_data.environment,
            source=alert_data.source,
            metric=alert_data.metric,
        )

        dedup_key = f"{settings.redis_key_prefix}:alert:dedup:{fingerprint}"

        idempotency_redis_key = f"{settings.redis_key_prefix}:idempotency:{idempotency_key}"

        cached_alert_id = await self.redis_store.get(dedup_key)

        if cached_alert_id is not None:
            existing_alert = await self.alert_repository.get_by_id(
                UUID(cached_alert_id),
            )

            if existing_alert is not None:
                return AlertResponse.model_validate(existing_alert)

        cached_idempotency_alert_id = await self.redis_store.get(
            idempotency_redis_key,
        )

        if cached_idempotency_alert_id is not None:
            existing_alert = await self.alert_repository.get_by_id(
                UUID(cached_idempotency_alert_id),
            )

            if existing_alert is not None:
                return AlertResponse.model_validate(existing_alert)

        try:
            async with self.session.begin():
                existing_key = await self.idempotency_repository.get_by_key(
                    idempotency_key,
                )

                if existing_key is not None:
                    existing_alert = await self.alert_repository.get_by_id(
                        existing_key.alert_id,
                    )

                    if existing_alert is not None:
                        return AlertResponse.model_validate(existing_alert)

                existing_alert = await self.alert_repository.get_by_fingerprint(
                    fingerprint,
                )

                if existing_alert is not None:
                    return AlertResponse.model_validate(existing_alert)

                incident_lock_key = (
                    f"{settings.redis_key_prefix}:"
                    f"incident:create:lock:{alert_data.service_id}:{alert_data.environment}"
                )
                incident_lock_token = secrets.token_urlsafe(32)

                incident_lock_acquired = await self.redis_store.acquire_lock(
                    incident_lock_key,
                    incident_lock_token,
                    ex=10,
                )

                if not incident_lock_acquired:
                    raise ServiceUnavailableError(
                        "Alert is currently being processed. Please try again."
                    )

                try:
                    incident = await self.incident_repository.get_open_by_service_and_environment(
                        service_id=alert_data.service_id,
                        environment=alert_data.environment,
                    )

                    if incident is None:
                        incident = Incident(
                            title=f"{alert_data.source} {alert_data.metric} alert",
                            description=(
                                f"{alert_data.metric} exceeded the configured "
                                f"threshold in {alert_data.environment}."
                            ),
                            service_id=alert_data.service_id,
                            environment=alert_data.environment,
                            severity=alert_data.severity,
                        )

                        incident = await self.incident_repository.create(incident)

                finally:
                    await self.redis_store.release_lock(
                        incident_lock_key,
                        incident_lock_token,
                    )

                alert = Alert(
                    **alert_data.model_dump(),
                    fingerprint=fingerprint,
                    incident_id=incident.id,
                )

                alert = await self.alert_repository.create(alert)

                idempotency_record = IdempotencyKey(
                    key=idempotency_key,
                    alert_id=alert.id,
                )

                await self.idempotency_repository.create(
                    idempotency_record,
                )

                await self.redis_store.set(
                    idempotency_redis_key,
                    str(alert.id),
                    ex=settings.alert_idempotency_window,
                )

                await self.redis_store.set(
                    dedup_key,
                    str(alert.id),
                    ex=settings.alert_dedup_window,
                )

        except IntegrityError as exc:
            error = str(exc.orig)

            if "ix_idempotency_keys_key" in error:
                existing_key = await self.idempotency_repository.get_by_key(
                    idempotency_key,
                )

                if existing_key is not None:
                    existing_alert = await self.alert_repository.get_by_id(
                        existing_key.alert_id,
                    )

                    if existing_alert is not None:
                        return AlertResponse.model_validate(existing_alert)

                raise ConflictError(
                    "The idempotency key has already been used.",
                ) from exc
            raise

        return AlertResponse.model_validate(alert)

    async def get_alert(
        self,
        alert_id: UUID,
    ) -> AlertResponse:
        alert = await self.alert_repository.get_by_id(alert_id)

        if alert is None:
            raise AlertNotFoundError(alert_id)

        return AlertResponse.model_validate(alert)

    async def get_incident_alerts(
        self,
        incident_id: UUID,
    ) -> list[AlertResponse]:
        alerts = await self.alert_repository.list_by_incident(
            incident_id,
        )

        return [AlertResponse.model_validate(alert) for alert in alerts]
