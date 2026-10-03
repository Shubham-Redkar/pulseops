from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.idempotency_key import IdempotencyKey


class IdempotencyRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self,
        idempotency_key: IdempotencyKey,
    ) -> IdempotencyKey:
        self.session.add(idempotency_key)
        await self.session.flush()

        return idempotency_key

    async def get_by_key(
        self,
        key: str,
    ) -> IdempotencyKey | None:
        stmt = select(IdempotencyKey).where(IdempotencyKey.key == key)

        return await self.session.scalar(stmt)
