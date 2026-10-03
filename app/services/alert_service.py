from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import AlertNotFoundError
from ..core.fingerprinting import generate_alert_fingerprint
from ..db.models import Alert, IdempotencyKey, Incident
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
    ) -> None:
        self.session = session
        self.alert_repository = alert_repository
        self.incident_repository = incident_repository
        self.idempotency_repository = idempotency_repository

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

            await self.idempotency_repository.create(idempotency_record)

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
