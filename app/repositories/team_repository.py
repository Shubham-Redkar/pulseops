from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.models.team import Team
from ..types.team import TeamUpdateData


class TeamRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, team: Team) -> Team:
        self.session.add(team)

        await self.session.flush()

        return team

    async def get_all(self) -> list[Team]:
        stmt = select(Team)

        result = await self.session.scalars(stmt)

        return list(result.all())

    async def get_by_id(self, team_id: UUID) -> Team | None:
        stmt = select(Team).where(Team.id == team_id)

        return await self.session.scalar(stmt)

    async def update(self, team_id: UUID, team_data: TeamUpdateData) -> Team | None:
        if not team_data:
            return await self.get_by_id(team_id)

        stmt = update(Team).where(Team.id == team_id).values(**team_data).returning(Team)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def delete(self, team_id: UUID) -> bool:
        stmt = delete(Team).where(Team.id == team_id).returning(Team.id)

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none() is not None
