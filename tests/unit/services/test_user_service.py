from collections.abc import Generator
from uuid import uuid4

import pytest

from app.core.exceptions import UserNotFoundError
from app.schemas.enums import UserRole
from app.schemas.user import CreateUserRequest, UpdateUserRequest
from app.services.user_service import UserService, users


@pytest.fixture
def user_service() -> Generator[UserService]:
    users.clear()

    service = UserService()

    yield service

    users.clear()


@pytest.mark.asyncio
async def test_create_user(user_service: UserService):
    user_data = CreateUserRequest(
        username="john",
        email="john@example.com",
        password="john123",
        role=UserRole.ADMIN,
    )

    result = await user_service.create_user(user_data)

    assert result.id is not None
    assert result.username == "john"
    assert result.email == "john@example.com"
    assert result.role == "admin"
    assert result.created_at is not None
    assert result.updated_at is not None
    assert result.created_at == result.updated_at
    assert result.id in users
    assert users[result.id] == result


@pytest.mark.asyncio
async def test_get_users_empty(user_service: UserService):
    result = await user_service.get_users()

    assert result == []


@pytest.mark.asyncio
async def test_get_users(user_service: UserService):
    first_user = await user_service.create_user(
        CreateUserRequest(
            username="john",
            email="john@example.com",
            password="john123",
            role=UserRole.ADMIN,
        )
    )

    second_user = await user_service.create_user(
        CreateUserRequest(
            username="jane", email="jane@example.com", password="jane123", role=UserRole.VIEWER
        )
    )

    result = await user_service.get_users()

    assert len(result) == 2
    assert first_user in result
    assert second_user in result


@pytest.mark.asyncio
async def test_get_user(user_service: UserService):
    created_user = await user_service.create_user(
        CreateUserRequest(
            username="john",
            email="john@example.com",
            password="john123",
            role=UserRole.ADMIN,
        )
    )

    result = await user_service.get_user(created_user.id)

    assert result == created_user
    assert result.id == created_user.id


@pytest.mark.asyncio
async def test_get_user_not_found(user_service: UserService):
    user_id = uuid4()

    with pytest.raises(
        UserNotFoundError,
        match=f"User with ID '{user_id}' not found",
    ):
        await user_service.get_user(user_id)


@pytest.mark.asyncio
async def test_update_user(user_service: UserService):
    created_user = await user_service.create_user(
        CreateUserRequest(
            username="john",
            email="john@example.com",
            password="john123",
            role=UserRole.ADMIN,
        )
    )

    original_created_at = created_user.created_at

    updated_user = await user_service.update_user(
        created_user.id,
        UpdateUserRequest(
            username="john-updated", email="john.updated@example.com", role=UserRole.VIEWER
        ),
    )

    assert updated_user.id == created_user.id
    assert updated_user.username == "john-updated"
    assert updated_user.email == "john.updated@example.com"
    assert updated_user.role == "viewer"
    assert updated_user.created_at == original_created_at
    assert updated_user.updated_at is not None


@pytest.mark.asyncio
async def test_update_user_only_updates_provided_fields(
    user_service: UserService,
):
    created_user = await user_service.create_user(
        CreateUserRequest(
            username="john",
            email="john@example.com",
            password="john123",
            role=UserRole.ADMIN,
        )
    )

    original_email = created_user.email
    original_role = created_user.role
    original_created_at = created_user.created_at

    updated_user = await user_service.update_user(
        created_user.id,
        UpdateUserRequest(
            username="john-updated",
        ),
    )

    assert updated_user.username == "john-updated"
    assert updated_user.email == original_email
    assert updated_user.role == original_role
    assert updated_user.created_at == original_created_at
    assert updated_user.updated_at is not None


@pytest.mark.asyncio
async def test_update_user_not_found(user_service: UserService):
    user_id = uuid4()

    with pytest.raises(
        UserNotFoundError,
        match=f"User with ID '{user_id}' not found",
    ):
        await user_service.update_user(
            user_id,
            UpdateUserRequest(
                username="john-updated",
            ),
        )


@pytest.mark.asyncio
async def test_delete_user(user_service: UserService):
    created_user = await user_service.create_user(
        CreateUserRequest(
            username="john",
            email="john@example.com",
            password="john123",
            role=UserRole.ADMIN,
        )
    )

    assert created_user.id in users

    result = await user_service.delete_user(created_user.id)

    assert result is None
    assert created_user.id not in users


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service: UserService):
    user_id = uuid4()

    with pytest.raises(
        UserNotFoundError,
        match=f"User with ID '{user_id}' not found",
    ):
        await user_service.delete_user(user_id)
