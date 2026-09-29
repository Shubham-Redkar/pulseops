from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.exceptions import ConflictError, UnauthorizedError
from ..core.security import (
    create_access_token,
    generate_email_verification_token,
    generate_password_reset_token,
    generate_refresh_token,
    hash_email_verification_token,
    hash_password,
    hash_password_reset_token,
    hash_refresh_token,
    verify_password,
)
from ..db.models import (
    EmailVerificationToken,
    PasswordResetToken,
    RefreshToken,
    User,
)
from ..repositories import (
    EmailVerificationTokenRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    UserRepository,
)
from ..schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from ..schemas.enums import UserRole
from ..schemas.user import UserResponse


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
        password_reset_token_repository: PasswordResetTokenRepository,
        email_verification_token_repository: EmailVerificationTokenRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository
        self.password_reset_token_repository = password_reset_token_repository
        self.email_verification_token_repository = email_verification_token_repository

    async def register(
        self,
        data: RegisterRequest,
    ) -> UserResponse:
        existing_user = await self.user_repository.get_by_username(str(data.username))

        if existing_user:
            raise ConflictError("Username already exists.")

        existing_user = await self.user_repository.get_by_email(data.email)

        if existing_user:
            raise ConflictError("Email already exists.")

        password_hash = hash_password(data.password.get_secret_value())

        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            email=data.email,
            password_hash=password_hash,
            role=UserRole.VIEWER,
            team_id=None,
            email_verified=False,
            is_active=True,
        )

        try:
            user = await self.user_repository.create(user)

            raw_token = generate_email_verification_token()

            print(f"EMAIL VERIFICATION TOKEN: {raw_token}")

            token_hash = hash_email_verification_token(raw_token)

            now = datetime.now(UTC)

            verification_token = EmailVerificationToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=now
                + timedelta(minutes=settings.email_verification_token_expire_minutes),
                used_at=None,
            )

            await self.email_verification_token_repository.create(
                verification_token,
            )

            await self.session.commit()
            await self.session.refresh(user)

        except IntegrityError as exc:
            await self.session.rollback()

            error = str(exc.orig)

            if "ix_users_username" in error:
                raise ConflictError("Username already exists.") from exc

            if "ix_users_email" in error:
                raise ConflictError("Email already exists.") from exc

            raise

        return UserResponse.model_validate(user)

    async def login(
        self,
        data: LoginRequest,
    ) -> TokenResponse:
        user = await self.user_repository.get_by_username(str(data.username))

        if not user:
            raise UnauthorizedError("Invalid username or password.")

        if not user.is_active:
            raise UnauthorizedError("User account is inactive.")

        now = datetime.now(UTC)

        if user.locked_until is not None:
            if user.locked_until > now:
                raise UnauthorizedError("Account is temporarily locked.")

            user.locked_until = None
            user.failed_login_attempts = 0

        if not verify_password(
            data.password.get_secret_value(),
            user.password_hash,
        ):
            user.failed_login_attempts += 1

            if user.failed_login_attempts >= settings.account_login_attempts:
                user.locked_until = now + timedelta(minutes=settings.account_lockout_minutes)

            await self.session.commit()

            raise UnauthorizedError("Invalid username or password.")

        if not user.email_verified:
            raise UnauthorizedError("Email address is not verified.")

        user.failed_login_attempts = 0
        user.locked_until = None

        access_token = create_access_token(str(user.id))

        refresh_token = generate_refresh_token()

        refresh_token_hash = hash_refresh_token(refresh_token)

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
        )

        try:
            await self.refresh_token_repository.create(refresh_token=refresh_token_record)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("Unable to create refresh token.") from exc

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_token=refresh_token,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
        )

    async def refresh(self, data: RefreshTokenRequest) -> TokenResponse:
        raw_refresh_token = data.refresh_token.get_secret_value()

        token_hash = hash_refresh_token(raw_refresh_token)

        refresh_token_record = await self.refresh_token_repository.get_by_hash(token_hash)

        if not refresh_token_record:
            raise UnauthorizedError("Invalid refresh token.")

        now = datetime.now(UTC)

        if refresh_token_record.revoked_at is not None:
            raise UnauthorizedError("Invalid refresh token.")

        if refresh_token_record.expires_at <= now:
            raise UnauthorizedError("Refresh token has expired.")

        user = await self.user_repository.get_by_id(refresh_token_record.user_id)

        if not user:
            raise UnauthorizedError("Invalid refresh token.")

        access_token = create_access_token(str(user.id))

        new_refresh_token = generate_refresh_token()
        new_refresh_token_hash = hash_refresh_token(new_refresh_token)

        new_refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=new_refresh_token_hash,
            expires_at=now + timedelta(days=settings.refresh_token_expire_days),
        )

        try:
            await self.refresh_token_repository.revoke(refresh_token_record)

            await self.refresh_token_repository.create(refresh_token=new_refresh_token_record)

            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("Unable to rotate refresh token.") from exc

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            refresh_token=new_refresh_token,
            refresh_expires_in=settings.refresh_token_expire_days * 24 * 60 * 60,
        )

    async def logout(self, data: RefreshTokenRequest) -> None:
        raw_refresh_token = data.refresh_token.get_secret_value()

        token_hash = hash_refresh_token(raw_refresh_token)

        refresh_token_record = await self.refresh_token_repository.get_by_hash(token_hash)

        if not refresh_token_record:
            raise UnauthorizedError("Invalid refresh token.")

        now = datetime.now(UTC)

        if refresh_token_record.revoked_at is not None:
            raise UnauthorizedError("Invalid refresh token.")

        if refresh_token_record.expires_at <= now:
            raise UnauthorizedError("Refresh token has expired.")

        await self.refresh_token_repository.revoke(refresh_token_record)
        await self.session.commit()

    async def change_password(
        self,
        current_user: User,
        data: ChangePasswordRequest,
    ) -> None:
        if not verify_password(
            data.current_password.get_secret_value(),
            current_user.password_hash,
        ):
            raise UnauthorizedError("Current password is incorrect.")

        if verify_password(
            data.new_password.get_secret_value(),
            current_user.password_hash,
        ):
            raise ConflictError("New password must be different from the current password.")

        current_user.password_hash = hash_password(data.new_password.get_secret_value())

        await self.refresh_token_repository.revoke_all_for_user(current_user.id)

        await self.session.commit()

    async def forgot_password(
        self,
        data: ForgotPasswordRequest,
    ) -> None:
        user = await self.user_repository.get_by_email(data.email)

        if not user:
            return None

        raw_token = generate_password_reset_token()

        token_hash = hash_password_reset_token(raw_token)

        now = datetime.now(UTC)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=now + timedelta(minutes=settings.password_reset_token_expire_minutes),
            used_at=None,
        )

        try:
            await self.password_reset_token_repository.invalidate_unused_for_user(user.id)
            await self.password_reset_token_repository.create(reset_token)
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("Unable to create password reset token.") from exc

    async def reset_password(
        self,
        data: ResetPasswordRequest,
    ) -> None:

        raw_token = data.reset_token.get_secret_value()

        token_hash = hash_password_reset_token(raw_token)

        reset_token = await self.password_reset_token_repository.get_by_hash(
            token_hash,
        )

        now = datetime.now(UTC)

        if not reset_token or reset_token.used_at is not None or reset_token.expires_at <= now:
            raise UnauthorizedError("Invalid or expired password reset token.")

        user = await self.user_repository.get_by_id(reset_token.user_id)

        if not user:
            raise UnauthorizedError("Invalid or expired password reset token.")

        if verify_password(
            data.new_password.get_secret_value(),
            user.password_hash,
        ):
            raise ConflictError("New password must be different from the current password.")

        user.password_hash = hash_password(data.new_password.get_secret_value())

        reset_token.used_at = now

        await self.refresh_token_repository.revoke_all_for_user(user.id)

        try:
            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("Unable to reset password.") from exc

    async def verify_email(
        self,
        data: VerifyEmailRequest,
    ) -> None:
        raw_token = data.token.get_secret_value()

        token_hash = hash_email_verification_token(raw_token)

        verification_token = await self.email_verification_token_repository.get_by_hash(
            token_hash,
        )

        now = datetime.now(UTC)

        if (
            not verification_token
            or verification_token.used_at is not None
            or verification_token.expires_at <= now
        ):
            raise UnauthorizedError("Invalid or expired email verification token.")

        user = await self.user_repository.get_by_id(
            verification_token.user_id,
        )

        if not user:
            raise UnauthorizedError("Invalid or expired email verification token.")

        if user.email_verified:
            raise ConflictError("Email is already verified.")

        user.email_verified = True
        verification_token.used_at = now

        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("Unable to verify email.") from exc
