from typing import cast
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import IncidentNotFoundError
from ..db.models.incident import Incident
from ..repositories.incident_repository import IncidentRepository
from ..schemas.incident import (
    CreateIncidentRequest,
    IncidentResponse,
    UpdateIncidentRequest,
)
from ..types.incident import IncidentUpdateData


class IncidentService:
    def __init__(
        self,
        session: AsyncSession,
        repository: IncidentRepository,
    ) -> None:
        self.session = session
        self.repository = repository

    async def create_incident(
        self,
        incident_data: CreateIncidentRequest,
    ) -> IncidentResponse:
        incident = Incident(
            id=uuid4(),
            **incident_data.model_dump(),
        )

        async with self.session.begin():
            incident = await self.repository.create(incident)

        return IncidentResponse.model_validate(incident)

    async def get_incidents(self) -> list[IncidentResponse]:
        incidents = await self.repository.get_all()

        return [IncidentResponse.model_validate(incident) for incident in incidents]

    async def get_incident(
        self,
        incident_id: UUID,
    ) -> IncidentResponse:
        if (incident := await self.repository.get_by_id(incident_id)) is None:
            raise IncidentNotFoundError(incident_id)

        return IncidentResponse.model_validate(incident)

    async def update_incident(
        self,
        incident_id: UUID,
        incident_data: UpdateIncidentRequest,
    ) -> IncidentResponse:
        update_data = cast(
            IncidentUpdateData,
            incident_data.model_dump(exclude_unset=True),
        )

        async with self.session.begin():
            if (
                incident := await self.repository.update(
                    incident_id,
                    update_data,
                )
            ) is None:
                raise IncidentNotFoundError(incident_id)

        return IncidentResponse.model_validate(incident)

    async def delete_incident(
        self,
        incident_id: UUID,
    ) -> None:
        async with self.session.begin():
            deleted = await self.repository.delete(incident_id)

            if not deleted:
                raise IncidentNotFoundError(incident_id)
