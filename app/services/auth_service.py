from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.exceptions import ConflictError, UnauthorizedError
from ..core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from ..db.models.refresh_token import RefreshToken
from ..db.models.user import User
from ..repositories.refresh_token_repository import RefreshTokenRepository
from ..repositories.user_repository import UserRepository
from ..schemas.auth import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse
from ..schemas.enums import UserRole
from ..schemas.user import UserResponse


class AuthService:
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def register(
        self,
        data: RegisterRequest,
    ) -> UserResponse:
        existing_user = await self.user_repository.get_by_username(data.username)

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
        )

        try:
            user = await self.user_repository.create(user)
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
        user = await self.user_repository.get_by_username(data.username)

        if not user:
            raise UnauthorizedError("Invalid username or password.")

        if not verify_password(
            data.password.get_secret_value(),
            user.password_hash,
        ):
            raise UnauthorizedError("Invalid username or password.")

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
