from collections.abc import Generator
from uuid import uuid4

import pytest

from app.core.exceptions import TeamNotFoundError
from app.schemas.team import CreateTeamRequest, UpdateTeamRequest
from app.services.team_service import TeamService, teams


@pytest.fixture
def team_service() -> Generator[TeamService]:
    teams.clear()

    service = TeamService()

    yield service

    teams.clear()


@pytest.mark.asyncio
async def test_create_team(team_service: TeamService):
    team_data = CreateTeamRequest(
        name="Payments Team",
        description=("Owns payment processing services and ensures reliable payment operations."),
    )

    result = await team_service.create_team(team_data)

    assert result.id is not None
    assert result.name == "Payments Team"
    assert (
        result.description
        == "Owns payment processing services and ensures reliable payment operations."
    )
    assert result.created_at is not None
    assert result.updated_at is not None
    assert result.created_at == result.updated_at
    assert result.id in teams
    assert teams[result.id] == result


@pytest.mark.asyncio
async def test_get_teams_empty(team_service: TeamService):
    result = await team_service.get_teams()

    assert result == []


@pytest.mark.asyncio
async def test_get_teams(team_service: TeamService):
    first_team = await team_service.create_team(
        CreateTeamRequest(
            name="Payments Team",
            description="Owns payment processing.",
        )
    )

    second_team = await team_service.create_team(
        CreateTeamRequest(
            name="Users Team",
            description="Owns user management.",
        )
    )

    result = await team_service.get_teams()

    assert len(result) == 2
    assert first_team in result
    assert second_team in result


@pytest.mark.asyncio
async def test_get_team(team_service: TeamService):
    created_team = await team_service.create_team(
        CreateTeamRequest(
            name="Payments Team",
            description="Owns payment processing.",
        )
    )

    result = await team_service.get_team(created_team.id)

    assert result == created_team
    assert result.id == created_team.id


@pytest.mark.asyncio
async def test_get_team_not_found(team_service: TeamService):
    team_id = uuid4()

    with pytest.raises(
        TeamNotFoundError,
        match=f"Team with ID '{team_id}' not found.",
    ):
        await team_service.get_team(team_id)


@pytest.mark.asyncio
async def test_update_team(team_service: TeamService):
    created_team = await team_service.create_team(
        CreateTeamRequest(
            name="Payments Team",
            description="Owns payment processing.",
        )
    )

    original_created_at = created_team.created_at

    updated_team = await team_service.update_team(
        created_team.id,
        UpdateTeamRequest(
            name="Updated Payments Team",
            description="Updated payment processing team.",
        ),
    )

    assert updated_team.id == created_team.id
    assert updated_team.name == "Updated Payments Team"
    assert updated_team.description == "Updated payment processing team."
    assert updated_team.created_at == original_created_at
    assert updated_team.updated_at is not None


@pytest.mark.asyncio
async def test_update_team_only_updates_provided_fields(
    team_service: TeamService,
):
    created_team = await team_service.create_team(
        CreateTeamRequest(
            name="Payments Team",
            description="Owns payment processing.",
        )
    )

    original_description = created_team.description
    original_created_at = created_team.created_at

    updated_team = await team_service.update_team(
        created_team.id,
        UpdateTeamRequest(
            name="Updated Payments Team",
        ),
    )

    assert updated_team.name == "Updated Payments Team"
    assert updated_team.description == original_description
    assert updated_team.created_at == original_created_at
    assert updated_team.updated_at is not None


@pytest.mark.asyncio
async def test_update_team_not_found(team_service: TeamService):
    team_id = uuid4()

    with pytest.raises(
        TeamNotFoundError,
        match=f"Team with ID '{team_id}' not found.",
    ):
        await team_service.update_team(
            team_id,
            UpdateTeamRequest(
                name="Updated Payments Team",
            ),
        )


@pytest.mark.asyncio
async def test_delete_team(team_service: TeamService):
    created_team = await team_service.create_team(
        CreateTeamRequest(
            name="Payments Team",
            description="Owns payment processing.",
        )
    )

    assert created_team.id in teams

    result = await team_service.delete_team(created_team.id)

    assert result is None
    assert created_team.id not in teams


@pytest.mark.asyncio
async def test_delete_team_not_found(team_service: TeamService):
    team_id = uuid4()

    with pytest.raises(
        TeamNotFoundError,
        match=f"Team with ID '{team_id}' not found.",
    ):
        await team_service.delete_team(team_id)
