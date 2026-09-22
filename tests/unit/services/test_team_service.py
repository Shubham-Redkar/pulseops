from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import ConflictError, TeamNotFoundError
from app.db.models.team import Team
from app.schemas.team import CreateTeamRequest, UpdateTeamRequest
from app.services.team_service import TeamService


def create_team_model(
    name: str = "Payments Team",
    description: str = "Owns payment processing.",
) -> Team:
    now = datetime.now(UTC)

    return Team(
        id=uuid4(),
        name=name,
        description=description,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_team(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    now = datetime.now(UTC)

    team = Team(
        id=uuid4(),
        name="Payments Team",
        description="Owns payment processing.",
        created_at=now,
        updated_at=now,
    )

    mock_team_repository.create.return_value = team

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    result = await service.create_team(
        CreateTeamRequest(
            name="Payments Team",
            description="Owns payment processing.",
        )
    )

    assert result.id == team.id
    assert result.name == "Payments Team"
    assert result.description == "Owns payment processing."
    assert result.created_at == now
    assert result.updated_at == now

    mock_team_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_team_duplicate_name(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    from sqlalchemy.exc import IntegrityError

    original_error = Exception('duplicate key value violates unique constraint "ix_teams_name"')

    mock_team_repository.create.side_effect = IntegrityError(
        statement="INSERT INTO teams",
        params={},
        orig=original_error,
    )

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    with pytest.raises(
        ConflictError,
        match="A team with this name already exists.",
    ):
        await service.create_team(
            CreateTeamRequest(
                name="Payments Team",
                description="Owns payment processing.",
            )
        )

    mock_team_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_teams(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    first_team = create_team_model(
        name="Payments Team",
        description="Owns payment processing.",
    )

    second_team = create_team_model(
        name="Users Team",
        description="Owns user management.",
    )

    mock_team_repository.get_all.return_value = (
        [first_team, second_team],
        2,
    )

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    result = await service.get_teams(
        limit=20,
        offset=0,
    )

    assert result.items
    assert len(result.items) == 2
    assert result.total == 2
    assert result.limit == 20
    assert result.offset == 0

    assert result.items[0].id == first_team.id
    assert result.items[0].name == "Payments Team"

    assert result.items[1].id == second_team.id
    assert result.items[1].name == "Users Team"

    mock_team_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_get_teams_empty(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    mock_team_repository.get_all.return_value = (
        [],
        0,
    )

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    result = await service.get_teams(
        limit=20,
        offset=0,
    )

    assert result.items == []
    assert result.total == 0
    assert result.limit == 20
    assert result.offset == 0

    mock_team_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_get_team(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    team = create_team_model()

    mock_team_repository.get_by_id.return_value = team

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    result = await service.get_team(team.id)

    assert result.id == team.id
    assert result.name == team.name
    assert result.description == team.description
    assert result.created_at == team.created_at
    assert result.updated_at == team.updated_at

    mock_team_repository.get_by_id.assert_awaited_once_with(team.id)


@pytest.mark.asyncio
async def test_get_team_not_found(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    team_id = uuid4()

    mock_team_repository.get_by_id.return_value = None

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    with pytest.raises(
        TeamNotFoundError,
        match=f"Team with ID '{team_id}' was not found.",
    ):
        await service.get_team(team_id)

    mock_team_repository.get_by_id.assert_awaited_once_with(team_id)


@pytest.mark.asyncio
async def test_update_team(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    team = create_team_model()

    updated_team = Team(
        id=team.id,
        name="Updated Payments Team",
        description="Updated payment processing team.",
        created_at=team.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_team_repository.update.return_value = updated_team

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    result = await service.update_team(
        team.id,
        UpdateTeamRequest(
            name="Updated Payments Team",
            description="Updated payment processing team.",
        ),
    )

    assert result.id == team.id
    assert result.name == "Updated Payments Team"
    assert result.description == "Updated payment processing team."
    assert result.created_at == team.created_at
    assert result.updated_at == updated_team.updated_at

    mock_team_repository.update.assert_awaited_once_with(
        team.id,
        {
            "name": "Updated Payments Team",
            "description": "Updated payment processing team.",
        },
    )


@pytest.mark.asyncio
async def test_update_team_only_provided_fields(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    team = create_team_model()

    updated_team = Team(
        id=team.id,
        name="Updated Payments Team",
        description=team.description,
        created_at=team.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_team_repository.update.return_value = updated_team

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    result = await service.update_team(
        team.id,
        UpdateTeamRequest(
            name="Updated Payments Team",
        ),
    )

    assert result.id == team.id
    assert result.name == "Updated Payments Team"
    assert result.description == team.description

    mock_team_repository.update.assert_awaited_once_with(
        team.id,
        {
            "name": "Updated Payments Team",
        },
    )


@pytest.mark.asyncio
async def test_update_team_not_found(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    team_id = uuid4()

    mock_team_repository.update.return_value = None

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    with pytest.raises(
        TeamNotFoundError,
        match=f"Team with ID '{team_id}' was not found.",
    ):
        await service.update_team(
            team_id,
            UpdateTeamRequest(
                name="Updated Payments Team",
            ),
        )

    mock_team_repository.update.assert_awaited_once_with(
        team_id,
        {
            "name": "Updated Payments Team",
        },
    )


@pytest.mark.asyncio
async def test_delete_team(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    team_id = uuid4()

    mock_team_repository.delete.return_value = True

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    result = await service.delete_team(team_id)

    assert result is None

    mock_team_repository.delete.assert_awaited_once_with(team_id)


@pytest.mark.asyncio
async def test_delete_team_not_found(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    team_id = uuid4()

    mock_team_repository.delete.return_value = False

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    with pytest.raises(
        TeamNotFoundError,
        match=f"Team with ID '{team_id}' was not found.",
    ):
        await service.delete_team(team_id)

    mock_team_repository.delete.assert_awaited_once_with(team_id)


@pytest.mark.asyncio
async def test_create_team_unexpected_integrity_error(
    mock_session: MagicMock,
    mock_team_repository: MagicMock,
) -> None:
    from sqlalchemy.exc import IntegrityError

    original_error = Exception("some unexpected database constraint")

    mock_team_repository.create.side_effect = IntegrityError(
        statement="INSERT INTO teams",
        params={},
        orig=original_error,
    )

    service = TeamService(
        session=mock_session,
        repository=mock_team_repository,
    )

    with pytest.raises(IntegrityError):
        await service.create_team(
            CreateTeamRequest(
                name="Payments Team",
                description="Owns payment processing.",
            )
        )

    mock_team_repository.create.assert_awaited_once()
