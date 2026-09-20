from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.service import Service
from ..types.service import ServiceUpdateData


class ServiceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, service: Service) -> Service:
        self.session.add(service)

        await self.session.flush()

        return service

    async def get_all(self) -> list[Service]:
        stmt = select(Service)

        result = await self.session.scalars(stmt)

        return list(result.all())

    async def get_by_id(self, service_id: UUID) -> Service | None:
        stmt = select(Service).where(Service.id == service_id)

        return await self.session.scalar(stmt)

    async def update(self, service_id: UUID, service_data: ServiceUpdateData) -> Service | None:
        if not service_data:
            return await self.get_by_id(service_id)

        stmt = (
            update(Service)
            .where(Service.id == service_id)
            .values(**service_data)
            .returning(Service)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def delete(self, service_id: UUID) -> bool:
        stmt = delete(Service).where(Service.id == service_id).returning(Service.id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None
