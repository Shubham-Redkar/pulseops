from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Team
from app.repositories.team_repository import TeamRepository


@pytest.mark.asyncio
async def test_create_team(test_session: AsyncSession, team_repository: TeamRepository):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    result = await team_repository.create(team)
    await test_session.commit()

    assert result.id is not None
    assert result.name == "Payments Team"
    assert result.description == "Owns payment processing."


@pytest.mark.asyncio
async def test_get_by_id(test_session: AsyncSession, team_repository: TeamRepository):
    team = Team(name="Payments Team", description="Owns payment processing.")

    await team_repository.create(team)
    await test_session.commit()

    result = await team_repository.get_by_id(team.id)

    assert result is not None
    assert result.id == team.id
    assert result.name == "Payments Team"


@pytest.mark.asyncio
async def test_get_all(test_session: AsyncSession, team_repository: TeamRepository):
    first_team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    second_team = Team(
        name="Users Team",
        description="Owns user management.",
    )

    await team_repository.create(first_team)
    await team_repository.create(second_team)
    await test_session.commit()

    teams, total = await team_repository.get_all(
        limit=20,
        offset=0,
    )

    assert len(teams) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_get_all_pagination(
    test_session: AsyncSession,
    team_repository: TeamRepository,
):
    for name in ["Team A", "Team B", "Team C"]:
        await team_repository.create(
            Team(
                name=name,
                description=f"{name} description",
            )
        )

    await test_session.commit()

    teams, total = await team_repository.get_all(
        limit=2,
        offset=0,
    )

    assert len(teams) == 2
    assert total == 3


@pytest.mark.asyncio
async def test_update_team(
    test_session: AsyncSession,
    team_repository: TeamRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    await team_repository.create(team)
    await test_session.commit()

    result = await team_repository.update(
        team.id,
        {
            "name": "Updated Payments Team",
            "description": "Updated description.",
        },
    )

    await test_session.commit()

    assert result is not None
    assert result.id == team.id
    assert result.name == "Updated Payments Team"
    assert result.description == "Updated description."


@pytest.mark.asyncio
async def test_update_team_not_found(
    team_repository: TeamRepository,
):
    result = await team_repository.update(
        uuid4(),
        {
            "name": "Does Not Exist",
        },
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_team_empty_values(
    test_session: AsyncSession,
    team_repository: TeamRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    await team_repository.create(team)
    await test_session.commit()

    result = await team_repository.update(
        team.id,
        {},
    )

    assert result is not None
    assert result.id == team.id
    assert result.name == "Payments Team"


@pytest.mark.asyncio
async def test_delete_team(
    test_session: AsyncSession,
    team_repository: TeamRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    await team_repository.create(team)
    await test_session.commit()

    result = await team_repository.delete(team.id)

    await test_session.commit()

    assert result is True

    deleted_team = await team_repository.get_by_id(team.id)

    assert deleted_team is None


@pytest.mark.asyncio
async def test_delete_team_not_found(
    team_repository: TeamRepository,
):
    result = await team_repository.delete(uuid4())

    assert result is False
