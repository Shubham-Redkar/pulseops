from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.user import User
from ..types.user import UserUpdateData


class UserRepository:
    """
    Repository for user persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        self.session.add(user)

        await self.session.flush()

        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(User).where(User.id == user_id)

        return await self.session.scalar(stmt)

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[Sequence[User], int]:
        count_stmt = select(func.count()).select_from(User)

        total = await self.session.scalar(count_stmt)

        stmt = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.scalars(stmt)

        return result.all(), total or 0

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)

        return await self.session.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)

        return await self.session.scalar(stmt)

    async def update(
        self,
        user_id: UUID,
        user_data: UserUpdateData,
    ) -> User | None:
        if not user_data:
            return await self.get_by_id(user_id)

        stmt = update(User).where(User.id == user_id).values(**user_data).returning(User)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def delete(self, user_id: UUID) -> bool:
        stmt = delete(User).where(User.id == user_id).returning(User.id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None
