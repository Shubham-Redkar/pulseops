from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.enums import UserRole


@pytest.mark.asyncio
async def test_create_user(
    test_session: AsyncSession,
    user_repository: UserRepository,
):
    user = User(
        username="alice",
        email="alice@example.com",
        password_hash="hashed-password",
        role=UserRole.VIEWER,
    )

    result = await user_repository.create(user)
    await test_session.commit()

    assert result.id is not None
    assert result.username == "alice"
    assert result.email == "alice@example.com"
    assert result.password_hash == "hashed-password"
    assert result.role == UserRole.VIEWER


@pytest.mark.asyncio
async def test_get_by_id(
    test_session: AsyncSession,
    user_repository: UserRepository,
):
    user = User(
        username="alice",
        email="alice@example.com",
        password_hash="hashed-password",
        role=UserRole.VIEWER,
    )

    await user_repository.create(user)
    await test_session.commit()

    result = await user_repository.get_by_id(user.id)

    assert result is not None
    assert result.id == user.id
    assert result.username == "alice"
    assert result.email == "alice@example.com"


@pytest.mark.asyncio
async def test_get_all(
    test_session: AsyncSession,
    user_repository: UserRepository,
):
    first_user = User(
        username="alice",
        email="alice@example.com",
        password_hash="hashed-password-1",
        role=UserRole.VIEWER,
    )

    second_user = User(
        username="bob",
        email="bob@example.com",
        password_hash="hashed-password-2",
        role=UserRole.ANALYST,
    )

    await user_repository.create(first_user)
    await user_repository.create(second_user)
    await test_session.commit()

    users, total = await user_repository.get_all(
        limit=20,
        offset=0,
    )

    assert len(users) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_get_all_pagination(
    test_session: AsyncSession,
    user_repository: UserRepository,
):
    for username in ["alice", "bob", "charlie"]:
        await user_repository.create(
            User(
                username=username,
                email=f"{username}@example.com",
                password_hash="hashed-password",
                role=UserRole.VIEWER,
            )
        )

    await test_session.commit()

    users, total = await user_repository.get_all(
        limit=2,
        offset=0,
    )

    assert len(users) == 2
    assert total == 3


@pytest.mark.asyncio
async def test_update_user(
    test_session: AsyncSession,
    user_repository: UserRepository,
):
    user = User(
        username="alice",
        email="alice@example.com",
        password_hash="hashed-password",
        role=UserRole.VIEWER,
    )

    await user_repository.create(user)
    await test_session.commit()

    result = await user_repository.update(
        user.id,
        {
            "username": "updated-alice",
            "email": "updated@example.com",
            "role": UserRole.ANALYST,
        },
    )

    await test_session.commit()

    assert result is not None
    assert result.id == user.id
    assert result.username == "updated-alice"
    assert result.email == "updated@example.com"
    assert result.role == UserRole.ANALYST


@pytest.mark.asyncio
async def test_update_user_not_found(
    user_repository: UserRepository,
):
    result = await user_repository.update(
        uuid4(),
        {
            "username": "does-not-exist",
        },
    )

    assert result is None


@pytest.mark.asyncio
async def test_update_user_empty_values(
    test_session: AsyncSession,
    user_repository: UserRepository,
):
    user = User(
        username="alice",
        email="alice@example.com",
        password_hash="hashed-password",
        role=UserRole.VIEWER,
    )

    await user_repository.create(user)
    await test_session.commit()

    result = await user_repository.update(
        user.id,
        {},
    )

    assert result is not None
    assert result.id == user.id
    assert result.username == "alice"
    assert result.email == "alice@example.com"


@pytest.mark.asyncio
async def test_delete_user(
    test_session: AsyncSession,
    user_repository: UserRepository,
):
    user = User(
        username="alice",
        email="alice@example.com",
        password_hash="hashed-password",
        role=UserRole.VIEWER,
    )

    await user_repository.create(user)
    await test_session.commit()

    result = await user_repository.delete(user.id)

    await test_session.commit()

    assert result is True

    deleted_user = await user_repository.get_by_id(user.id)

    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_user_not_found(
    user_repository: UserRepository,
):
    result = await user_repository.delete(uuid4())

    assert result is False
