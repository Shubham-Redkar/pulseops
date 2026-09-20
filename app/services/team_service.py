from typing import cast
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.team import CreateTeamRequest, TeamResponse, UpdateTeamRequest

from ..core.exceptions import TeamNotFoundError
from ..db.models.team import Team
from ..repositories.team_repository import TeamRepository
from ..types.team import TeamUpdateData

teams: dict[UUID, TeamResponse] = {}


class TeamService:
    def __init__(self, session: AsyncSession, repository: TeamRepository) -> None:
        self.session = session
        self.repository = repository

    async def create_team(self, team_data: CreateTeamRequest) -> TeamResponse:
        team = Team(
            id=uuid4(),
            **team_data.model_dump(),
        )

        async with self.session.begin():
            team = await self.repository.create(team)

        return TeamResponse.model_validate(team)

    async def get_teams(self) -> list[TeamResponse]:
        teams = await self.repository.get_all()

        return [TeamResponse.model_validate(team) for team in teams]

    async def get_team(self, team_id: UUID) -> TeamResponse:
        if (team := await self.repository.get_by_id(team_id)) is None:
            raise TeamNotFoundError(team_id)

        return TeamResponse.model_validate(team)

    async def update_team(self, team_id: UUID, team_data: UpdateTeamRequest) -> TeamResponse:
        update_data = cast(TeamUpdateData, team_data.model_dump(exclude_unset=True))

        async with self.session.begin():
            if (team := await self.repository.update(team_id, update_data)) is None:
                raise TeamNotFoundError(team_id)

        return TeamResponse.model_validate(team)

    async def delete_team(self, team_id: UUID) -> None:
        async with self.session.begin():
            deleted = await self.repository.delete(team_id)

            if not deleted:
                raise TeamNotFoundError(team_id)
