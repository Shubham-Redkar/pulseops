from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.service import Service
from ..types.service import ServiceUpdateData


class ServiceRepository:
    """
    Repository for service persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, service: Service) -> Service:
        self.session.add(service)

        await self.session.flush()

        return service

    async def get_by_id(self, service_id: UUID) -> Service | None:
        stmt = select(Service).where(Service.id == service_id)

        return await self.session.scalar(stmt)

    async def get_all(
        self,
        limit: int,
        offset: int,
    ) -> tuple[list[Service], int]:
        count_stmt = select(func.count()).select_from(Service)

        total = await self.session.scalar(count_stmt)

        stmt = select(Service).order_by(Service.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.scalars(stmt)

        return list(result.all()), total or 0

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
