from typing import cast
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserNotFoundError
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse
from app.types.user import UserUpdateData


class UserService:
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
            id=uuid4(),
            **user_data.model_dump(),
        )

        async with self.session.begin():
            user = await self.repository.create(user)

        return UserResponse.model_validate(user)

    async def get_users(self) -> list[UserResponse]:
        users = await self.repository.get_all()

        return [UserResponse.model_validate(user) for user in users]

    async def get_user(self, user_id: UUID) -> UserResponse:
        if (user := await self.repository.get_by_id(user_id)) is None:
            raise UserNotFoundError(user_id)

        return UserResponse.model_validate(user)

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
