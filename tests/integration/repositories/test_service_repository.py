from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Service, Team
from app.repositories.service_repository import ServiceRepository


@pytest.mark.asyncio
async def test_create_service(
    test_session: AsyncSession,
    service_repository: ServiceRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.commit()

    service = Service(
        name="payment-service",
        description="Another description.",
        team_id=team.id,
    )

    result = await service_repository.create(service)
    await test_session.commit()

    assert result.id is not None
    assert result.name == "payment-service"
    assert result.description == "Another description."
    assert result.team_id == team.id


@pytest.mark.asyncio
async def test_get_by_id(
    test_session: AsyncSession,
    service_repository: ServiceRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.commit()

    service = Service(
        name="payment-service",
        description="Another description.",
        team_id=team.id,
    )

    await service_repository.create(service)
    await test_session.commit()

    result = await service_repository.get_by_id(service.id)

    assert result is not None
    assert result.id == service.id
    assert result.name == "payment-service"
    assert result.description == "Another description."
    assert result.team_id == team.id


@pytest.mark.asyncio
async def test_get_all(
    test_session: AsyncSession,
    service_repository: ServiceRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.commit()

    first_service = Service(
        name="payment-service",
        description="Payment processing service.",
        team_id=team.id,
    )

    second_service = Service(
        name="user-service",
        description="User management service.",
        team_id=team.id,
    )

    await service_repository.create(first_service)
    await service_repository.create(second_service)
    await test_session.commit()

    services, total = await service_repository.get_all(
        limit=20,
        offset=0,
    )

    assert len(services) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_get_all_pagination(
    test_session: AsyncSession,
    service_repository: ServiceRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.commit()

    for name in [
        "payment-service",
        "user-service",
        "notification-service",
    ]:
        await service_repository.create(
            Service(
                name=name,
                description=f"{name} description.",
                team_id=team.id,
            )
        )

    await test_session.commit()

    services, total = await service_repository.get_all(
        limit=2,
        offset=0,
    )

    assert len(services) == 2
    assert total == 3


@pytest.mark.asyncio
async def test_update_service(
    test_session: AsyncSession,
    service_repository: ServiceRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.commit()

    service = Service(
        name="payment-service",
        description="Payment processing service.",
        team_id=team.id,
    )

    await service_repository.create(service)
    await test_session.commit()

    result = await service_repository.update(
        service.id,
        {
            "name": "updated-payment-service",
            "description": "Updated payment service.",
        },
    )

    await test_session.commit()

    assert result is not None
    assert result.id == service.id
    assert result.name == "updated-payment-service"
    assert result.description == "Updated payment service."
    assert result.team_id == team.id


@pytest.mark.asyncio
async def test_update_service_not_found(
    service_repository: ServiceRepository,
):
    result = await service_repository.update(
        uuid4(),
        {
            "name": "does-not-exist",
        },
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_service_empty_values(
    test_session: AsyncSession,
    service_repository: ServiceRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.commit()

    service = Service(
        name="payment-service",
        description="Payment processing service.",
        team_id=team.id,
    )

    await service_repository.create(service)
    await test_session.commit()

    result = await service_repository.update(
        service.id,
        {},
    )

    assert result is not None
    assert result.id == service.id
    assert result.name == "payment-service"
    assert result.description == "Payment processing service."
    assert result.team_id == team.id


@pytest.mark.asyncio
async def test_delete_service(
    test_session: AsyncSession,
    service_repository: ServiceRepository,
):
    team = Team(
        name="Payments Team",
        description="Owns payment processing.",
    )

    test_session.add(team)
    await test_session.commit()

    service = Service(
        name="payment-service",
        description="Payment processing service.",
        team_id=team.id,
    )

    await service_repository.create(service)
    await test_session.commit()

    result = await service_repository.delete(service.id)

    await test_session.commit()

    assert result is True

    deleted_service = await service_repository.get_by_id(service.id)

    assert deleted_service is None


@pytest.mark.asyncio
async def test_delete_service_not_found(
    service_repository: ServiceRepository,
):
    result = await service_repository.delete(uuid4())

    assert result is False
