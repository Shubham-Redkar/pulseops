import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.incident_repository import IncidentRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository


@pytest.fixture
def team_repository(test_session: AsyncSession) -> TeamRepository:
    return TeamRepository(test_session)


@pytest.fixture
def service_repository(test_session: AsyncSession) -> ServiceRepository:
    return ServiceRepository(test_session)


@pytest.fixture
def incident_repository(test_session: AsyncSession) -> IncidentRepository:
    return IncidentRepository(test_session)


@pytest.fixture
def user_repository(test_session: AsyncSession) -> UserRepository:
    return UserRepository(test_session)
