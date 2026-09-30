from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pydantic import SecretStr

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password
from app.db.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.schemas.enums import UserRole
from app.services.auth_service import AuthService


def create_user_model(
    username: str = "john",
    email: str = "john@example.com",
    role: UserRole = UserRole.ADMIN,
    first_name: str = "John",
    last_name: str = "Doe",
    email_verified: bool = True,
    is_active: bool = True,
    password: str = "SecurePassword456!",
) -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid4(),
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        team_id=None,
        is_active=is_active,
        email_verified=email_verified,
        created_at=now,
        updated_at=now,
        locked_until=None,
        failed_login_attempts=0,
    )


@pytest.mark.asyncio
async def test_register_success(mock_session: MagicMock, mock_user_repository: MagicMock) -> None:
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_user_repository.get_by_username = AsyncMock(return_value=None)
    mock_user_repository.get_by_email = AsyncMock(return_value=None)

    mock_user = create_user_model()
    mock_user_repository.create = AsyncMock(return_value=mock_user)

    mock_email_repo = MagicMock()
    mock_email_repo.create = AsyncMock()

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=MagicMock(),
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=mock_email_repo,
    )

    req = RegisterRequest(
        first_name="John",
        last_name="Doe",
        username="john",
        email="john@example.com",
        password=SecretStr("SecurePassword456!"),
    )

    result = await service.register(req)

    assert result.username == "john"
    mock_user_repository.create.assert_awaited_once()
    mock_email_repo.create.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_duplicate_username(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_username = AsyncMock(return_value=create_user_model())

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=MagicMock(),
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    req = RegisterRequest(
        first_name="John",
        last_name="Doe",
        username="john",
        email="john@example.com",
        password=SecretStr("SecurePassword456!"),
    )

    with pytest.raises(ConflictError):
        await service.register(req)


@pytest.mark.asyncio
async def test_login_success(mock_session: MagicMock, mock_user_repository: MagicMock) -> None:
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_user = create_user_model(password="SecurePassword456!")
    mock_user_repository.get_by_username = AsyncMock(return_value=mock_user)

    mock_refresh_repo = MagicMock()
    mock_refresh_repo.create = AsyncMock()

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_repo,
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    req = LoginRequest(
        username="john",
        password=SecretStr("SecurePassword456!"),
    )

    res = await service.login(req)

    assert res.access_token is not None
    assert res.refresh_token is not None
    mock_refresh_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_invalid_password(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_user = create_user_model(password="CorrectPassword123!")
    mock_user_repository.get_by_username = AsyncMock(return_value=mock_user)

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=MagicMock(),
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    req = LoginRequest(
        username="john",
        password=SecretStr("WrongPassword123!"),
    )

    with pytest.raises(UnauthorizedError):
        await service.login(req)

    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_unverified_email(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user = create_user_model(password="SecurePassword456!", email_verified=False)
    mock_user_repository.get_by_username = AsyncMock(return_value=mock_user)

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=MagicMock(),
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    req = LoginRequest(
        username="john",
        password=SecretStr("SecurePassword456!"),
    )

    with pytest.raises(UnauthorizedError):
        await service.login(req)


@pytest.mark.asyncio
async def test_refresh_success(mock_session: MagicMock, mock_user_repository: MagicMock) -> None:
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    mock_refresh_repo = MagicMock()
    mock_token_record = MagicMock()
    mock_token_record.revoked_at = None
    mock_token_record.expires_at = datetime.now(UTC) + timedelta(days=1)
    mock_token_record.user_id = uuid4()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token_record)
    mock_refresh_repo.revoke = AsyncMock()
    mock_refresh_repo.create = AsyncMock()

    mock_user = create_user_model()
    mock_user_repository.get_by_id = AsyncMock(return_value=mock_user)

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_repo,
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    req = RefreshTokenRequest(refresh_token=SecretStr("valid-token"))
    res = await service.refresh(req)

    assert res.access_token is not None
    assert res.refresh_token is not None
    mock_refresh_repo.revoke.assert_awaited_once()
    mock_refresh_repo.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_invalid_token(mock_session: MagicMock) -> None:
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=None)

    service = AuthService(
        session=mock_session,
        user_repository=MagicMock(),
        refresh_token_repository=mock_refresh_repo,
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    with pytest.raises(UnauthorizedError):
        await service.refresh(RefreshTokenRequest(refresh_token=SecretStr("invalid-token")))


@pytest.mark.asyncio
async def test_logout_success(mock_session: MagicMock) -> None:
    mock_session.commit = AsyncMock()
    mock_refresh_repo = MagicMock()
    mock_token_record = MagicMock()
    mock_token_record.revoked_at = None
    mock_token_record.expires_at = datetime.now(UTC) + timedelta(days=1)
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token_record)
    mock_refresh_repo.revoke = AsyncMock()

    service = AuthService(
        session=mock_session,
        user_repository=MagicMock(),
        refresh_token_repository=mock_refresh_repo,
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    await service.logout(RefreshTokenRequest(refresh_token=SecretStr("valid-token")))

    mock_refresh_repo.revoke.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_change_password_success(mock_session: MagicMock) -> None:
    mock_session.commit = AsyncMock()
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.revoke_all_for_user = AsyncMock()

    current_user = create_user_model(password="OldPassword123!")

    service = AuthService(
        session=mock_session,
        user_repository=MagicMock(),
        refresh_token_repository=mock_refresh_repo,
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=MagicMock(),
    )

    req = ChangePasswordRequest(
        current_password=SecretStr("OldPassword123!"),
        new_password=SecretStr("NewPassword456!"),
    )

    await service.change_password(current_user, req)

    mock_refresh_repo.revoke_all_for_user.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_forgot_password_success(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_session.commit = AsyncMock()
    mock_user = create_user_model()
    mock_user_repository.get_by_email = AsyncMock(return_value=mock_user)

    mock_reset_repo = MagicMock()
    mock_reset_repo.invalidate_unused_for_user = AsyncMock()
    mock_reset_repo.create = AsyncMock()

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=MagicMock(),
        password_reset_token_repository=mock_reset_repo,
        email_verification_token_repository=MagicMock(),
    )

    req = ForgotPasswordRequest(email="john@example.com")
    await service.forgot_password(req)

    mock_reset_repo.invalidate_unused_for_user.assert_awaited_once()
    mock_reset_repo.create.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reset_password_success(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_session.commit = AsyncMock()

    mock_reset_repo = MagicMock()
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=15)
    mock_token.user_id = uuid4()
    mock_reset_repo.get_by_hash = AsyncMock(return_value=mock_token)

    mock_user = create_user_model(password="OldPassword123!")
    mock_user_repository.get_by_id = AsyncMock(return_value=mock_user)

    mock_refresh_repo = MagicMock()
    mock_refresh_repo.revoke_all_for_user = AsyncMock()

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=mock_refresh_repo,
        password_reset_token_repository=mock_reset_repo,
        email_verification_token_repository=MagicMock(),
    )

    req = ResetPasswordRequest(
        reset_token=SecretStr("valid-token"),
        new_password=SecretStr("NewPassword456!"),
    )

    await service.reset_password(req)

    mock_refresh_repo.revoke_all_for_user.assert_awaited_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_verify_email_success(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_session.commit = AsyncMock()

    mock_verify_repo = MagicMock()
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=15)
    mock_token.user_id = uuid4()
    mock_verify_repo.get_by_hash = AsyncMock(return_value=mock_token)

    mock_user = create_user_model(email_verified=False)
    mock_user_repository.get_by_id = AsyncMock(return_value=mock_user)

    service = AuthService(
        session=mock_session,
        user_repository=mock_user_repository,
        refresh_token_repository=MagicMock(),
        password_reset_token_repository=MagicMock(),
        email_verification_token_repository=mock_verify_repo,
    )

    req = VerifyEmailRequest(token=SecretStr("valid-token"))
    await service.verify_email(req)

    assert mock_user.email_verified is True
    assert mock_token.used_at is not None
    mock_session.commit.assert_awaited_once()
