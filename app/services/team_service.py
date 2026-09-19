from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.team import CreateTeamRequest, TeamResponse, UpdateTeamRequest

from ..core.exceptions import TeamNotFoundError

teams: dict[UUID, TeamResponse] = {}


class TeamService:
    async def create_team(self, team_data: CreateTeamRequest) -> TeamResponse:
        now = datetime.now(UTC)

        team_id = uuid4()

        team = TeamResponse(id=team_id, **team_data.model_dump(), created_at=now, updated_at=now)

        teams[team_id] = team

        return team

    async def get_teams(self) -> list[TeamResponse]:
        return list(teams.values())

    async def get_team(self, team_id: UUID) -> TeamResponse:
        if (team := teams.get(team_id)) is None:
            raise TeamNotFoundError(f"Team with ID '{team_id}' not found.")

        return team

    async def update_team(self, team_id: UUID, team_data: UpdateTeamRequest) -> TeamResponse:
        if (team := teams.get(team_id)) is None:
            raise TeamNotFoundError(f"Team with ID '{team_id}' not found.")

        updates = team_data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(team, field, value)

        team.updated_at = datetime.now(UTC)

        return team

    async def delete_team(self, team_id: UUID) -> None:
        if team_id not in teams:
            raise TeamNotFoundError(f"Team with ID '{team_id}' not found.")

        teams.pop(team_id)


team_service = TeamService()
