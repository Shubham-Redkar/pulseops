from typing import cast
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import ConflictError, TeamNotFoundError
from ..db.models.team import Team
from ..repositories.team_repository import TeamRepository
from ..schemas.base import PaginatedResponse
from ..schemas.team import CreateTeamRequest, TeamResponse, UpdateTeamRequest
from ..types.team import TeamUpdateData


class TeamService:
    """
    Manage team business operations.
    """

    def __init__(self, session: AsyncSession, repository: TeamRepository) -> None:
        self.session = session
        self.repository = repository

    async def create_team(self, team_data: CreateTeamRequest) -> TeamResponse:
        team = Team(
            **team_data.model_dump(),
        )

        try:
            async with self.session.begin():
                team = await self.repository.create(team)
        except IntegrityError as exc:
            if "ix_teams_name" in str(exc.orig):
                raise ConflictError("A team with this name already exists.") from exc

            raise

        return TeamResponse.model_validate(team)

    async def get_teams(self, *, limit: int, offset: int) -> PaginatedResponse[TeamResponse]:
        teams, total = await self.repository.get_all(limit=limit, offset=offset)

        return PaginatedResponse[TeamResponse](
            items=[TeamResponse.model_validate(team) for team in teams],
            limit=limit,
            offset=offset,
            total=total,
        )

    async def get_team(self, team_id: UUID) -> TeamResponse:
        team = await self.repository.get_by_id(team_id)

        if team is None:
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
