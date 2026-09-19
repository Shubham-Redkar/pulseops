from datetime import UTC, datetime
from uuid import UUID, uuid4

from ..core.exceptions import IncidentNotFoundError
from ..schemas.incident import CreateIncidentRequest, IncidentResponse, UpdateIncidentRequest

incidents: dict[UUID, IncidentResponse] = {}


class IncidentService:
    async def create_incident(self, incident_data: CreateIncidentRequest) -> IncidentResponse:
        now = datetime.now(UTC)
        incident_id = uuid4()

        incident = IncidentResponse(
            id=incident_id, **incident_data.model_dump(), created_at=now, updated_at=now
        )

        incidents[incident_id] = incident

        return incident

    async def get_incidents(self) -> list[IncidentResponse]:
        return list(incidents.values())

    async def get_incident(self, incident_id: UUID) -> IncidentResponse:
        if (incident := incidents.get(incident_id)) is None:
            raise IncidentNotFoundError(incident_id)

        return incident

    async def update_incident(
        self, incident_id: UUID, incident_data: UpdateIncidentRequest
    ) -> IncidentResponse:
        if (incident := incidents.get(incident_id)) is None:
            raise IncidentNotFoundError(incident_id)

        updates = incident_data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(incident, field, value)

        incident.updated_at = datetime.now(UTC)

        return incident

    async def delete_incident(self, incident_id: UUID) -> None:
        if incident_id not in incidents:
            raise IncidentNotFoundError(incident_id)

        incidents.pop(incident_id)


incident_service = IncidentService()
