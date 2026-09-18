from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.schemas.user import CreateUserRequest, UpdateUserRequest, UserResponse

users: dict[UUID, UserResponse] = {}


class UserService:
    async def create_user(self, user_data: CreateUserRequest) -> UserResponse:
        now = datetime.now(UTC)

        user_id = uuid4()

        user = UserResponse(id=user_id, **user_data.model_dump(), created_at=now, updated_at=now)

        users[user_id] = user

        return user

    async def get_users(self) -> list[UserResponse]:
        return list(users.values())

    async def get_user(self, user_id: UUID) -> UserResponse:
        if (user := users.get(user_id)) is None:
            raise ValueError("User not found")

        return user

    async def update_user(self, user_id: UUID, user_data: UpdateUserRequest) -> UserResponse:
        if (user := users.get(user_id)) is None:
            raise ValueError("User not found")

        updates = user_data.model_dump(exclude_unset=True)

        for field, value in updates.items():
            setattr(user, field, value)

        user.updated_at = datetime.now(UTC)

        return user

    async def delete_user(self, user_id: UUID) -> None:
        if user_id not in users:
            raise ValueError("User not found")

        users.pop(user_id)


user_service = UserService()
