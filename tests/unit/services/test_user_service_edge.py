from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.exceptions import UserNotFoundError
from app.services.user_service import UserService
from tests.unit.services.test_auth_service import create_user_model


@pytest.mark.asyncio
async def test_update_user_status_not_found(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_id = AsyncMock(return_value=None)
    service = UserService(
        mock_session,
        mock_user_repository,
        MagicMock(),
    )
    with pytest.raises(UserNotFoundError):
        await service.update_user_status(uuid4(), False)


@pytest.mark.asyncio
async def test_update_user_status_same_status(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    user = create_user_model(is_active=True)
    mock_user_repository.get_by_id = AsyncMock(return_value=user)
    service = UserService(
        mock_session,
        mock_user_repository,
        MagicMock(),
    )
    res = await service.update_user_status(user.id, True)
    assert res.is_active is True
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_user_status_to_inactive(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    user = create_user_model(is_active=True)
    mock_user_repository.get_by_id = AsyncMock(return_value=user)

    mock_refresh_repo = MagicMock()
    mock_refresh_repo.revoke_all_for_user = AsyncMock()

    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    service = UserService(
        mock_session,
        mock_user_repository,
        mock_refresh_repo,
    )
    res = await service.update_user_status(user.id, False)

    assert res.is_active is False
    mock_refresh_repo.revoke_all_for_user.assert_awaited_once_with(user.id)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_status_to_active(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    user = create_user_model(is_active=False)
    mock_user_repository.get_by_id = AsyncMock(return_value=user)

    mock_refresh_repo = MagicMock()
    mock_refresh_repo.revoke_all_for_user = AsyncMock()

    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    service = UserService(
        mock_session,
        mock_user_repository,
        mock_refresh_repo,
    )
    res = await service.update_user_status(user.id, True)

    assert res.is_active is True
    mock_refresh_repo.revoke_all_for_user.assert_not_called()
    mock_session.commit.assert_awaited_once()
