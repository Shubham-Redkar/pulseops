from uuid import UUID

from fastapi import APIRouter, status

from ...schemas.incident import (
    CreateIncidentRequest,
    IncidentResponse,
    UpdateIncidentRequest,
)
from ..dependencies import IncidentServiceDep

router = APIRouter(
    prefix="/incidents",
    tags=["Incidents"],
)


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_incident(
    incident_data: CreateIncidentRequest,
    incident_service: IncidentServiceDep,
) -> IncidentResponse:
    return await incident_service.create_incident(incident_data)


@router.get(
    "",
    response_model=list[IncidentResponse],
)
async def get_incidents(
    incident_service: IncidentServiceDep,
) -> list[IncidentResponse]:
    return await incident_service.get_incidents()


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def get_incident(
    incident_id: UUID,
    incident_service: IncidentServiceDep,
) -> IncidentResponse:
    return await incident_service.get_incident(incident_id)


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
)
async def update_incident(
    incident_id: UUID,
    incident_data: UpdateIncidentRequest,
    incident_service: IncidentServiceDep,
) -> IncidentResponse:
    return await incident_service.update_incident(
        incident_id,
        incident_data,
    )


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_incident(
    incident_id: UUID,
    incident_service: IncidentServiceDep,
) -> None:
    await incident_service.delete_incident(incident_id)
