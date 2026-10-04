from typing import cast
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import (
    ConflictError,
    UserNotFoundError,
)
from ..core.security import hash_password
from ..core.types import UserUpdateData
from ..db.models.user import User
from ..repositories import (
    RefreshTokenRepository,
    UserRepository,
)
from ..schemas.base import PaginatedResponse
from ..schemas.user import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
)


class UserService:
    """
    Manage user business operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        refresh_token_repository: RefreshTokenRepository,
    ) -> None:
        self.session = session
        self.user_repository = user_repository
        self.refresh_token_repository = refresh_token_repository

    async def create_user(
        self,
        user_data: CreateUserRequest,
    ) -> UserResponse:
        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password.get_secret_value()),
            role=user_data.role,
            team_id=user_data.team_id,
        )

        try:
            if self.session.in_transaction():
                await self.session.commit()
            async with self.session.begin():
                user = await self.user_repository.create(user)
        except IntegrityError as exc:
            error = str(exc.orig)

            if "ix_users_username" in error:
                raise ConflictError(
                    "A user with this username already exists.",
                ) from exc

            if "ix_users_email" in error:
                raise ConflictError(
                    "A user with this email already exists.",
                ) from exc
            raise

        return UserResponse.model_validate(user)

    async def get_user(
        self,
        user_id: UUID,
    ) -> UserResponse:
        if (user := await self.user_repository.get_by_id(user_id)) is None:
            raise UserNotFoundError(user_id)

        return UserResponse.model_validate(user)

    async def get_users(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[UserResponse]:
        users, total = await self.user_repository.get_all(
            limit=limit,
            offset=offset,
        )

        return PaginatedResponse(
            items=[UserResponse.model_validate(user) for user in users],
            limit=limit,
            offset=offset,
            total=total,
        )

    async def update_user(
        self,
        user_id: UUID,
        user_data: UpdateUserRequest,
    ) -> UserResponse:
        update_data = cast(
            UserUpdateData,
            user_data.model_dump(exclude_unset=True),
        )

        try:
            if self.session.in_transaction():
                await self.session.commit()
            async with self.session.begin():
                if (
                    user := await self.user_repository.update(
                        user_id,
                        update_data,
                    )
                ) is None:
                    raise UserNotFoundError(user_id)
        except IntegrityError as exc:
            error = str(exc.orig)

            if "ix_users_username" in error:
                raise ConflictError(
                    "A user with this username already exists.",
                ) from exc

            if "ix_users_email" in error:
                raise ConflictError(
                    "A user with this email already exists.",
                ) from exc
            raise

        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: UUID) -> None:
        if self.session.in_transaction():
            await self.session.commit()
        async with self.session.begin():
            deleted = await self.user_repository.delete(user_id)

            if not deleted:
                raise UserNotFoundError(user_id)

    async def update_user_status(
        self,
        user_id: UUID,
        is_active: bool,
    ) -> UserResponse:
        user = await self.user_repository.get_by_id(user_id)

        if not user:
            raise UserNotFoundError(user_id)

        if user.is_active == is_active:
            return UserResponse.model_validate(user)

        try:
            if self.session.in_transaction():
                await self.session.commit()
            async with self.session.begin():
                user.is_active = is_active

                if not is_active:
                    await self.refresh_token_repository.revoke_all_for_user(user.id)
        except IntegrityError as exc:
            raise ConflictError(
                "Unable to update user status.",
            ) from exc

        return UserResponse.model_validate(user)
