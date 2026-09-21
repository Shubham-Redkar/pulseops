from uuid import UUID

from fastapi import APIRouter, Query, status

from ...api.dependencies import TeamServiceDep
from ...schemas.base import PaginatedResponse
from ...schemas.team import (
    CreateTeamRequest,
    TeamResponse,
    UpdateTeamRequest,
)

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.post(
    "",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_team(
    team_data: CreateTeamRequest,
    team_service: TeamServiceDep,
) -> TeamResponse:
    return await team_service.create_team(team_data)


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
)
async def get_team(
    team_id: UUID,
    team_service: TeamServiceDep,
) -> TeamResponse:
    return await team_service.get_team(team_id)


@router.get(
    "",
    response_model=PaginatedResponse[TeamResponse],
)
async def get_teams(
    team_service: TeamServiceDep,
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of teams to return.",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Number of teams to skip.",
    ),
) -> PaginatedResponse[TeamResponse]:
    return await team_service.get_teams(
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/{team_id}",
    response_model=TeamResponse,
)
async def update_team(
    team_id: UUID,
    team_data: UpdateTeamRequest,
    team_service: TeamServiceDep,
) -> TeamResponse:
    return await team_service.update_team(team_id, team_data)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_team(
    team_id: UUID,
    team_service: TeamServiceDep,
) -> None:
    await team_service.delete_team(team_id)
