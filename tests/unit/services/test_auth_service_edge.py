from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import SecretStr
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
)
from app.services.auth_service import AuthService
from tests.unit.services.test_auth_service import create_user_model


@pytest.mark.asyncio
async def test_register_email_exists(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_username = AsyncMock(return_value=None)
    mock_user_repository.get_by_email = AsyncMock(return_value=create_user_model())

    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    req = RegisterRequest(
        first_name="John",
        last_name="Doe",
        username="jjj",
        email="j@example.com",
        password=SecretStr("SecurePassword456!"),
    )

    with pytest.raises(ConflictError, match="Email already exists"):
        await service.register(req)


@pytest.mark.asyncio
async def test_register_integrity_error_username(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_username = AsyncMock(return_value=None)
    mock_user_repository.get_by_email = AsyncMock(return_value=None)

    mock_email_repo = MagicMock()
    mock_email_repo.create = AsyncMock()

    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        MagicMock(),
        mock_email_repo,
    )

    exc = IntegrityError("statement", "params", Exception("ix_users_username"))
    mock_session.commit = AsyncMock(side_effect=exc)
    mock_session.rollback = AsyncMock()

    req = RegisterRequest(
        first_name="John",
        last_name="Doe",
        username="jjj",
        email="j@example.com",
        password=SecretStr("SecurePassword456!"),
    )
    with pytest.raises(ConflictError, match="Username already exists"):
        await service.register(req)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_integrity_error_email(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_username = AsyncMock(return_value=None)
    mock_user_repository.get_by_email = AsyncMock(return_value=None)

    mock_email_repo = MagicMock()
    mock_email_repo.create = AsyncMock()

    service = AuthService(
        mock_session, mock_user_repository, MagicMock(), MagicMock(), mock_email_repo
    )

    exc = IntegrityError("statement", "params", Exception("ix_users_email"))
    mock_session.commit = AsyncMock(side_effect=exc)
    mock_session.rollback = AsyncMock()

    req = RegisterRequest(
        first_name="John",
        last_name="Doe",
        username="jjj",
        email="j@example.com",
        password=SecretStr("SecurePassword456!"),
    )
    with pytest.raises(ConflictError, match="Email already exists"):
        await service.register(req)


@pytest.mark.asyncio
async def test_register_integrity_error_other(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_username = AsyncMock(return_value=None)
    mock_user_repository.get_by_email = AsyncMock(return_value=None)

    mock_email_repo = MagicMock()
    mock_email_repo.create = AsyncMock()

    service = AuthService(
        mock_session, mock_user_repository, MagicMock(), MagicMock(), mock_email_repo
    )

    exc = IntegrityError("statement", "params", Exception("some_other_error"))
    mock_session.commit = AsyncMock(side_effect=exc)
    mock_session.rollback = AsyncMock()

    req = RegisterRequest(
        first_name="John",
        last_name="Doe",
        username="jjj",
        email="j@example.com",
        password=SecretStr("SecurePassword456!"),
    )
    with pytest.raises(IntegrityError):
        await service.register(req)


@pytest.mark.asyncio
async def test_login_user_not_found(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_username = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    req = LoginRequest(username="jjj", password=SecretStr("SecurePassword456!"))
    with pytest.raises(UnauthorizedError, match="Invalid username or password"):
        await service.login(req)


@pytest.mark.asyncio
async def test_login_user_inactive(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    user = create_user_model(is_active=False)
    mock_user_repository.get_by_username = AsyncMock(return_value=user)
    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    req = LoginRequest(username="jjj", password=SecretStr("SecurePassword456!"))
    with pytest.raises(UnauthorizedError, match="User account is inactive"):
        await service.login(req)


@pytest.mark.asyncio
async def test_login_account_locked(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    user = create_user_model()
    user.locked_until = datetime.now(UTC) + timedelta(minutes=10)
    mock_user_repository.get_by_username = AsyncMock(return_value=user)
    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    req = LoginRequest(username="jjj", password=SecretStr("SecurePassword456!"))
    with pytest.raises(UnauthorizedError, match="Account is temporarily locked"):
        await service.login(req)


@pytest.mark.asyncio
async def test_login_lockout_trigger(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    user = create_user_model(password="SecurePassword456!")
    user.failed_login_attempts = settings.account_login_attempts - 1
    mock_user_repository.get_by_username = AsyncMock(return_value=user)

    mock_session.commit = AsyncMock()

    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    req = LoginRequest(username="jjj", password=SecretStr("WrongPassword123!"))
    with pytest.raises(UnauthorizedError):
        await service.login(req)
    assert user.locked_until is not None


@pytest.mark.asyncio
async def test_login_integrity_error(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    user = create_user_model(password="SecurePassword456!")
    mock_user_repository.get_by_username = AsyncMock(return_value=user)

    mock_refresh_repo = MagicMock()
    exc = IntegrityError("stmt", "params", Exception("err"))
    mock_refresh_repo.create = AsyncMock(side_effect=exc)

    mock_session.rollback = AsyncMock()

    service = AuthService(
        mock_session,
        mock_user_repository,
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    req = LoginRequest(username="jjj", password=SecretStr("SecurePassword456!"))
    with pytest.raises(ConflictError, match="Unable to create refresh token"):
        await service.login(req)


@pytest.mark.asyncio
async def test_refresh_revoked(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.revoked_at = datetime.now(UTC)
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token)
    service = AuthService(
        mock_session,
        MagicMock(),
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Invalid refresh token"):
        await service.refresh(RefreshTokenRequest(refresh_token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_refresh_expired(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.revoked_at = None
    mock_token.expires_at = datetime.now(UTC) - timedelta(minutes=10)
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token)
    service = AuthService(
        mock_session,
        MagicMock(),
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Refresh token has expired"):
        await service.refresh(RefreshTokenRequest(refresh_token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_refresh_user_not_found(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_token = MagicMock()
    mock_token.revoked_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_user_repository.get_by_id = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        mock_user_repository,
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Invalid refresh token"):
        await service.refresh(RefreshTokenRequest(refresh_token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_refresh_integrity_error(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_token = MagicMock()
    mock_token.revoked_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_refresh_repo.revoke = AsyncMock()

    mock_user_repository.get_by_id = AsyncMock(return_value=create_user_model())

    exc = IntegrityError("stmt", "params", Exception("err"))
    mock_refresh_repo.create = AsyncMock(side_effect=exc)

    mock_session.rollback = AsyncMock()

    service = AuthService(
        mock_session,
        mock_user_repository,
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(ConflictError, match="Unable to rotate refresh token"):
        await service.refresh(RefreshTokenRequest(refresh_token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_logout_invalid(mock_session: MagicMock) -> None:
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        MagicMock(),
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Invalid refresh token"):
        await service.logout(RefreshTokenRequest(refresh_token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_logout_revoked(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.revoked_at = datetime.now(UTC)
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token)
    service = AuthService(
        mock_session,
        MagicMock(),
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Invalid refresh token"):
        await service.logout(RefreshTokenRequest(refresh_token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_logout_expired(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.revoked_at = None
    mock_token.expires_at = datetime.now(UTC) - timedelta(minutes=10)
    mock_refresh_repo = MagicMock()
    mock_refresh_repo.get_by_hash = AsyncMock(return_value=mock_token)
    service = AuthService(
        mock_session,
        MagicMock(),
        mock_refresh_repo,
        MagicMock(),
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Refresh token has expired"):
        await service.logout(RefreshTokenRequest(refresh_token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_change_password_incorrect(mock_session: MagicMock) -> None:
    service = AuthService(
        mock_session,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    user = create_user_model(password="OldPassword123!")
    req = ChangePasswordRequest(
        current_password=SecretStr("WrongPassword123!"), new_password=SecretStr("NewPassword123!")
    )
    with pytest.raises(UnauthorizedError, match="Current password is incorrect"):
        await service.change_password(user, req)


@pytest.mark.asyncio
async def test_change_password_same(mock_session: MagicMock) -> None:
    service = AuthService(
        mock_session,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    user = create_user_model(password="OldPassword123!")
    req = ChangePasswordRequest(
        current_password=SecretStr("OldPassword123!"), new_password=SecretStr("OldPassword123!")
    )
    with pytest.raises(ConflictError, match="New password must be different"):
        await service.change_password(user, req)


@pytest.mark.asyncio
async def test_forgot_password_user_not_found(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_email = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )
    await service.forgot_password(ForgotPasswordRequest(email="a@example.com"))


@pytest.mark.asyncio
async def test_forgot_password_integrity_error(
    mock_session: MagicMock, mock_user_repository: MagicMock
) -> None:
    mock_user_repository.get_by_email = AsyncMock(return_value=create_user_model())
    mock_reset_repo = MagicMock()
    mock_reset_repo.invalidate_unused_for_user = AsyncMock()
    exc = IntegrityError("stmt", "params", Exception("err"))
    mock_reset_repo.create = AsyncMock(side_effect=exc)

    mock_session.rollback = AsyncMock()

    service = AuthService(
        mock_session,
        mock_user_repository,
        MagicMock(),
        mock_reset_repo,
        MagicMock(),
    )
    with pytest.raises(ConflictError, match="Unable to create password reset token"):
        await service.forgot_password(ForgotPasswordRequest(email="a@example.com"))


@pytest.mark.asyncio
async def test_reset_password_invalid_token(mock_session: MagicMock) -> None:
    mock_reset_repo = MagicMock()
    mock_reset_repo.get_by_hash = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        MagicMock(),
        MagicMock(),
        mock_reset_repo,
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Invalid or expired"):
        await service.reset_password(
            ResetPasswordRequest(
                reset_token=SecretStr("token123"), new_password=SecretStr("NewPassword123!")
            )
        )


@pytest.mark.asyncio
async def test_reset_password_user_not_found(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_reset_repo = MagicMock()
    mock_reset_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_id = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        mock_user_repo,
        MagicMock(),
        mock_reset_repo,
        MagicMock(),
    )
    with pytest.raises(UnauthorizedError, match="Invalid or expired"):
        await service.reset_password(
            ResetPasswordRequest(
                reset_token=SecretStr("token123"), new_password=SecretStr("NewPassword123!")
            )
        )


@pytest.mark.asyncio
async def test_reset_password_same_password(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_reset_repo = MagicMock()
    mock_reset_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_id = AsyncMock(return_value=create_user_model(password="OldPassword123!"))
    service = AuthService(
        mock_session,
        mock_user_repo,
        MagicMock(),
        mock_reset_repo,
        MagicMock(),
    )
    with pytest.raises(ConflictError, match="New password must be different"):
        await service.reset_password(
            ResetPasswordRequest(
                reset_token=SecretStr("token123"), new_password=SecretStr("OldPassword123!")
            )
        )


@pytest.mark.asyncio
async def test_reset_password_integrity_error(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_reset_repo = MagicMock()
    mock_reset_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_id = AsyncMock(return_value=create_user_model(password="OldPassword123!"))

    mock_refresh_repo = MagicMock()
    mock_refresh_repo.revoke_all_for_user = AsyncMock()

    exc = IntegrityError("stmt", "params", Exception("err"))
    mock_session.commit = AsyncMock(side_effect=exc)
    mock_session.rollback = AsyncMock()

    service = AuthService(
        mock_session,
        mock_user_repo,
        mock_refresh_repo,
        mock_reset_repo,
        MagicMock(),
    )
    with pytest.raises(ConflictError, match="Unable to reset password"):
        await service.reset_password(
            ResetPasswordRequest(
                reset_token=SecretStr("token123"), new_password=SecretStr("NewPassword123!")
            )
        )


@pytest.mark.asyncio
async def test_verify_email_invalid_token(mock_session: MagicMock) -> None:
    mock_verify_repo = MagicMock()
    mock_verify_repo.get_by_hash = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        MagicMock(),
        MagicMock(),
        MagicMock(),
        mock_verify_repo,
    )
    with pytest.raises(UnauthorizedError, match="Invalid or expired"):
        await service.verify_email(VerifyEmailRequest(token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_verify_email_user_not_found(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_verify_repo = MagicMock()
    mock_verify_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_id = AsyncMock(return_value=None)
    service = AuthService(
        mock_session,
        mock_user_repo,
        MagicMock(),
        MagicMock(),
        mock_verify_repo,
    )
    with pytest.raises(UnauthorizedError, match="Invalid or expired"):
        await service.verify_email(VerifyEmailRequest(token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_verify_email_already_verified(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_verify_repo = MagicMock()
    mock_verify_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_id = AsyncMock(return_value=create_user_model(email_verified=True))
    service = AuthService(
        mock_session,
        mock_user_repo,
        MagicMock(),
        MagicMock(),
        mock_verify_repo,
    )
    with pytest.raises(ConflictError, match="Email is already verified"):
        await service.verify_email(VerifyEmailRequest(token=SecretStr("token123")))


@pytest.mark.asyncio
async def test_verify_email_integrity_error(mock_session: MagicMock) -> None:
    mock_token = MagicMock()
    mock_token.used_at = None
    mock_token.expires_at = datetime.now(UTC) + timedelta(minutes=10)
    mock_verify_repo = MagicMock()
    mock_verify_repo.get_by_hash = AsyncMock(return_value=mock_token)
    mock_user_repo = MagicMock()
    mock_user_repo.get_by_id = AsyncMock(return_value=create_user_model(email_verified=False))

    exc = IntegrityError("stmt", "params", Exception("err"))
    mock_session.commit = AsyncMock(side_effect=exc)
    mock_session.rollback = AsyncMock()

    service = AuthService(
        mock_session,
        mock_user_repo,
        MagicMock(),
        MagicMock(),
        mock_verify_repo,
    )
    with pytest.raises(ConflictError, match="Unable to verify email"):
        await service.verify_email(VerifyEmailRequest(token=SecretStr("token123")))
