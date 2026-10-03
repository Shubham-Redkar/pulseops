from uuid import UUID

from fastapi import APIRouter, Header, status

from ...core.rate_limit import check_alert_rate_limit
from ...schemas.alert import AlertResponse, CreateAlertRequest
from ..dependencies import (
    AdminOrAnalystUserDep,
    AlertServiceDep,
    CurrentUserDep,
    RedisStoreDep,
)

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_alert(
    current_user: AdminOrAnalystUserDep,
    alert_data: CreateAlertRequest,
    alert_service: AlertServiceDep,
    redis_store: RedisStoreDep,
    idempotency_key: str = Header(
        ...,
        alias="Idempotency-Key",
        min_length=1,
        max_length=255,
    ),
) -> AlertResponse:
    await check_alert_rate_limit(
        redis_store,
        current_user.id,
    )

    return await alert_service.create_alert(
        alert_data,
        idempotency_key,
    )


@router.get(
    "/incident/{incident_id}",
    response_model=list[AlertResponse],
)
async def list_alerts_by_incident(
    _: CurrentUserDep,
    incident_id: UUID,
    alert_service: AlertServiceDep,
) -> list[AlertResponse]:
    return await alert_service.get_incident_alerts(incident_id)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    _: CurrentUserDep,
    alert_id: UUID,
    alert_service: AlertServiceDep,
) -> AlertResponse:
    return await alert_service.get_alert(alert_id)
