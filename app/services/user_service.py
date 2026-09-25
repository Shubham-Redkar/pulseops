from typing import cast
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import ConflictError, UserNotFoundError
from ..core.security import hash_password
from ..db.models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.base import PaginatedResponse
from ..schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse
from ..types.user import UserUpdateData


class UserService:
    """
    Manage user business operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository: UserRepository,
    ) -> None:
        self.session = session
        self.repository = repository

    async def create_user(
        self,
        user_data: CreateUserRequest,
    ) -> UserResponse:

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password.get_secret_value()),
            role=user_data.role,
            team_id=user_data.team_id,
        )

        try:
            async with self.session.begin():
                user = await self.repository.create(user)
        except IntegrityError as exc:
            error = str(exc.orig)

            if "ix_users_username" in error:
                raise ConflictError("A user with this username already exists.") from exc

            if "ix_users_email" in error:
                raise ConflictError("A user with this email already exists.") from exc

            raise

        return UserResponse.model_validate(user)

    async def get_user(self, user_id: UUID) -> UserResponse:
        if (user := await self.repository.get_by_id(user_id)) is None:
            raise UserNotFoundError(user_id)

        return UserResponse.model_validate(user)

    async def get_users(
        self,
        limit: int,
        offset: int,
    ) -> PaginatedResponse[UserResponse]:
        users, total = await self.repository.get_all(
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
        async with self.session.begin():
            if (
                user := await self.repository.update(
                    user_id,
                    update_data,
                )
            ) is None:
                raise UserNotFoundError(user_id)

        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: UUID) -> None:
        async with self.session.begin():
            deleted = await self.repository.delete(user_id)

            if not deleted:
                raise UserNotFoundError(user_id)
