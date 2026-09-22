from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ConflictError, UserNotFoundError
from app.db.models.user import User
from app.schemas.enums import UserRole
from app.schemas.user import CreateUserRequest, UpdateUserRequest
from app.services.user_service import UserService


def create_user_model(
    username: str = "john",
    email: str = "john@example.com",
    role: UserRole = UserRole.ANALYST,
    team_id: UUID | None = None,
) -> User:
    now = datetime.now(UTC)

    return User(
        id=uuid4(),
        username=username,
        email=email,
        password_hash="hashed-password",
        role=role,
        team_id=team_id,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_user(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    team_id = uuid4()

    user = create_user_model(
        username="john",
        email="john@example.com",
        role=UserRole.ANALYST,
        team_id=team_id,
    )

    mock_user_repository.create.return_value = user

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    result = await service.create_user(
        CreateUserRequest(
            username="john",
            email="john@example.com",
            password="SecurePassword456!",
            role=UserRole.ANALYST,
            team_id=team_id,
        )
    )

    assert result.id == user.id
    assert result.username == "john"
    assert result.email == "john@example.com"
    assert result.role == UserRole.ANALYST
    assert result.team_id == team_id
    assert result.created_at == user.created_at
    assert result.updated_at == user.updated_at

    mock_user_repository.create.assert_awaited_once()

    created_user = mock_user_repository.create.call_args.args[0]

    assert created_user.username == "john"
    assert created_user.email == "john@example.com"
    assert created_user.role == UserRole.ANALYST
    assert created_user.team_id == team_id
    assert created_user.password_hash != "SecurePassword456!"


@pytest.mark.asyncio
async def test_create_user_duplicate_username(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    original_error = Exception('duplicate key value violates unique constraint "ix_users_username"')

    mock_user_repository.create.side_effect = IntegrityError(
        statement="INSERT INTO users",
        params={},
        orig=original_error,
    )

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    with pytest.raises(
        ConflictError,
        match="A user with this username already exists.",
    ):
        await service.create_user(
            CreateUserRequest(
                username="john",
                email="john@example.com",
                password="SecurePassword456!",
                role=UserRole.ANALYST,
            )
        )

    mock_user_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    original_error = Exception('duplicate key value violates unique constraint "ix_users_email"')

    mock_user_repository.create.side_effect = IntegrityError(
        statement="INSERT INTO users",
        params={},
        orig=original_error,
    )

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    with pytest.raises(
        ConflictError,
        match="A user with this email already exists.",
    ):
        await service.create_user(
            CreateUserRequest(
                username="john",
                email="john@example.com",
                password="SecurePassword456!",
                role=UserRole.ANALYST,
            )
        )

    mock_user_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_user(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    user = create_user_model()

    mock_user_repository.get_by_id.return_value = user

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    result = await service.get_user(user.id)

    assert result.id == user.id
    assert result.username == user.username
    assert result.email == user.email
    assert result.role == user.role
    assert result.team_id == user.team_id
    assert result.created_at == user.created_at
    assert result.updated_at == user.updated_at

    mock_user_repository.get_by_id.assert_awaited_once_with(user.id)


@pytest.mark.asyncio
async def test_get_user_not_found(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    user_id = uuid4()

    mock_user_repository.get_by_id.return_value = None

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    with pytest.raises(
        UserNotFoundError,
        match=f"User with ID '{user_id}' was not found.",
    ):
        await service.get_user(user_id)

    mock_user_repository.get_by_id.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_get_users(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    first_user = create_user_model(
        username="john",
        email="john@example.com",
    )

    second_user = create_user_model(
        username="jane",
        email="jane@example.com",
    )

    mock_user_repository.get_all.return_value = (
        [first_user, second_user],
        2,
    )

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    result = await service.get_users(
        limit=20,
        offset=0,
    )

    assert result.items
    assert len(result.items) == 2
    assert result.total == 2
    assert result.limit == 20
    assert result.offset == 0

    assert result.items[0].id == first_user.id
    assert result.items[0].username == "john"

    assert result.items[1].id == second_user.id
    assert result.items[1].username == "jane"

    mock_user_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_get_users_empty(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    mock_user_repository.get_all.return_value = (
        [],
        0,
    )

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    result = await service.get_users(
        limit=20,
        offset=0,
    )

    assert result.items == []
    assert result.total == 0
    assert result.limit == 20
    assert result.offset == 0

    mock_user_repository.get_all.assert_awaited_once_with(
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_update_user(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    user = create_user_model()

    updated_user = User(
        id=user.id,
        username="updated_john",
        email="updated@example.com",
        password_hash=user.password_hash,
        role=UserRole.ADMIN,
        team_id=user.team_id,
        created_at=user.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_user_repository.update.return_value = updated_user

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    result = await service.update_user(
        user.id,
        UpdateUserRequest(
            username="updated_john",
            email="updated@example.com",
            role=UserRole.ADMIN,
        ),
    )

    assert result.id == user.id
    assert result.username == "updated_john"
    assert result.email == "updated@example.com"
    assert result.role == UserRole.ADMIN
    assert result.team_id == user.team_id
    assert result.created_at == user.created_at
    assert result.updated_at == updated_user.updated_at

    mock_user_repository.update.assert_awaited_once_with(
        user.id,
        {
            "username": "updated_john",
            "email": "updated@example.com",
            "role": UserRole.ADMIN,
        },
    )


@pytest.mark.asyncio
async def test_update_user_only_provided_fields(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    user = create_user_model()

    updated_user = User(
        id=user.id,
        username="updated_john",
        email=user.email,
        password_hash=user.password_hash,
        role=user.role,
        team_id=user.team_id,
        created_at=user.created_at,
        updated_at=datetime.now(UTC),
    )

    mock_user_repository.update.return_value = updated_user

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    result = await service.update_user(
        user.id,
        UpdateUserRequest(
            username="updated_john",
        ),
    )

    assert result.id == user.id
    assert result.username == "updated_john"
    assert result.email == user.email
    assert result.role == user.role

    mock_user_repository.update.assert_awaited_once_with(
        user.id,
        {
            "username": "updated_john",
        },
    )


@pytest.mark.asyncio
async def test_update_user_not_found(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    user_id = uuid4()

    mock_user_repository.update.return_value = None

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    with pytest.raises(
        UserNotFoundError,
        match=f"User with ID '{user_id}' was not found.",
    ):
        await service.update_user(
            user_id,
            UpdateUserRequest(
                username="updated_john",
            ),
        )

    mock_user_repository.update.assert_awaited_once_with(
        user_id,
        {
            "username": "updated_john",
        },
    )


@pytest.mark.asyncio
async def test_delete_user(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    user_id = uuid4()

    mock_user_repository.delete.return_value = True

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    result = await service.delete_user(user_id)

    assert result is None

    mock_user_repository.delete.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_delete_user_not_found(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    user_id = uuid4()

    mock_user_repository.delete.return_value = False

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    with pytest.raises(
        UserNotFoundError,
        match=f"User with ID '{user_id}' was not found.",
    ):
        await service.delete_user(user_id)

    mock_user_repository.delete.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_create_user_unexpected_integrity_error(
    mock_session: MagicMock,
    mock_user_repository: MagicMock,
) -> None:
    from sqlalchemy.exc import IntegrityError

    original_error = Exception("some unexpected database constraint")

    mock_user_repository.create.side_effect = IntegrityError(
        statement="INSERT INTO users",
        params={},
        orig=original_error,
    )

    service = UserService(
        session=mock_session,
        repository=mock_user_repository,
    )

    with pytest.raises(IntegrityError):
        await service.create_user(
            CreateUserRequest(
                username="john",
                email="john@example.com",
                password="SecurePassword456!",
                role=UserRole.ADMIN,
                team_id=None,
            )
        )

    mock_user_repository.create.assert_awaited_once()
