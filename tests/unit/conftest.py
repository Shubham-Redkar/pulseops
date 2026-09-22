from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.incident_repository import IncidentRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository


@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock()

    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=transaction)
    transaction.__aexit__ = AsyncMock(return_value=False)

    session.begin.return_value = transaction

    return session


@pytest.fixture
def mock_team_repository() -> MagicMock:
    repository = MagicMock()

    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_all = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()

    return repository


@pytest.fixture
def mock_service_repository() -> MagicMock:
    repository = MagicMock(spec=ServiceRepository)

    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_all = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()

    return repository


@pytest.fixture
def mock_incident_repository() -> MagicMock:
    repository = MagicMock(spec=IncidentRepository)

    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_all = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()

    return repository


@pytest.fixture
def mock_user_repository() -> MagicMock:
    repository = MagicMock(spec=UserRepository)

    repository.create = AsyncMock()
    repository.get_by_id = AsyncMock()
    repository.get_all = AsyncMock()
    repository.update = AsyncMock()
    repository.delete = AsyncMock()

    return repository
