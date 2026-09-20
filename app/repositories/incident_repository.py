from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.incident import Incident
from ..types.incident import IncidentUpdateData


class IncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, incident: Incident) -> Incident:
        self.session.add(incident)

        await self.session.flush()

        return incident

    async def get_all(self) -> list[Incident]:
        stmt = select(Incident)

        result = await self.session.scalars(stmt)

        return list(result.all())

    async def get_by_id(self, incident_id: UUID) -> Incident | None:
        stmt = select(Incident).where(Incident.id == incident_id)

        return await self.session.scalar(stmt)

    async def update(self, incident_id: UUID, incident_data: IncidentUpdateData) -> Incident | None:
        if not incident_data:
            return await self.get_by_id(incident_id)

        stmt = (
            update(Incident)
            .where(Incident.id == incident_id)
            .values(**incident_data)
            .returning(Incident)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def delete(self, incident_id: UUID) -> bool:
        stmt = delete(Incident).where(Incident.id == incident_id).returning(Incident.id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None
