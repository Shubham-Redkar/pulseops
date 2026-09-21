from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.team import Team
from ..types.team import TeamUpdateData


class TeamRepository:
    """
    Repository for team persistence operations.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, team: Team) -> Team:
        self.session.add(team)

        await self.session.flush()

        return team

    async def get_by_id(self, team_id: UUID) -> Team | None:
        stmt = select(Team).where(Team.id == team_id)

        return await self.session.scalar(stmt)

    async def get_all(
        self,
        *,
        limit: int,
        offset: int,
    ) -> tuple[Sequence[Team], int]:
        count_stmt = select(func.count()).select_from(Team)

        total = await self.session.scalar(count_stmt)

        stmt = select(Team).order_by(Team.created_at.desc()).limit(limit).offset(offset)

        result = await self.session.scalars(stmt)

        return result.all(), total or 0

    async def update(self, team_id: UUID, values: TeamUpdateData) -> Team | None:
        if not values:
            return await self.get_by_id(team_id)

        stmt = update(Team).where(Team.id == team_id).values(**values).returning(Team)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def delete(self, team_id: UUID) -> bool:
        stmt = delete(Team).where(Team.id == team_id).returning(Team.id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None
