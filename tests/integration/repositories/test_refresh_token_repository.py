from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.refresh_token import RefreshToken
from app.db.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.schemas.enums import UserRole


async def create_test_user(
    test_session: AsyncSession,
) -> User:
    user = User(
        id=uuid4(),
        first_name="Test",
        last_name="User",
        username=f"test_{uuid4().hex[:8]}",
        email=f"{uuid4().hex[:8]}@example.com",
        password_hash="hashed-password",
        role=UserRole.VIEWER,
    )

    test_session.add(user)
    await test_session.flush()

    return user


@pytest.mark.asyncio
async def test_create_refresh_token(
    test_session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
):
    user = await create_test_user(test_session)

    refresh_token = RefreshToken(
        token_hash="test-token-hash",
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    result = await refresh_token_repository.create(refresh_token)

    assert result is refresh_token
    assert result.token_hash == "test-token-hash"

    await test_session.commit()

    stored = await test_session.get(RefreshToken, result.id)

    assert stored is not None
    assert stored.token_hash == "test-token-hash"
    assert stored.user_id == user.id
    assert stored.revoked_at is None


@pytest.mark.asyncio
async def test_get_by_hash(
    test_session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
):
    user = await create_test_user(test_session)

    refresh_token = RefreshToken(
        token_hash="test-token-hash",
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    await refresh_token_repository.create(refresh_token)

    result = await refresh_token_repository.get_by_hash(
        "test-token-hash",
    )

    assert result is not None
    assert result.id == refresh_token.id
    assert result.token_hash == "test-token-hash"
    assert result.user_id == user.id


@pytest.mark.asyncio
async def test_get_by_hash_not_found(
    refresh_token_repository: RefreshTokenRepository,
):
    result = await refresh_token_repository.get_by_hash(
        "does-not-exist",
    )

    assert result is None


@pytest.mark.asyncio
async def test_revoke_refresh_token(
    test_session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
):
    user = await create_test_user(test_session)

    refresh_token = RefreshToken(
        token_hash="test-token-hash",
        user_id=user.id,
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    await refresh_token_repository.create(refresh_token)

    assert refresh_token.revoked_at is None

    await refresh_token_repository.revoke(refresh_token)

    assert refresh_token.revoked_at is not None
    assert refresh_token.revoked_at.tzinfo is not None


@pytest.mark.asyncio
async def test_delete_expired_or_revoked(
    test_session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
):
    user = await create_test_user(test_session)

    now = datetime.now(UTC)

    active_token = RefreshToken(
        user_id=user.id,
        token_hash=f"active-{uuid4()}",
        expires_at=now + timedelta(days=1),
        revoked_at=None,
    )

    expired_token = RefreshToken(
        user_id=user.id,
        token_hash=f"expired-{uuid4()}",
        expires_at=now - timedelta(days=1),
        revoked_at=None,
    )

    revoked_token = RefreshToken(
        user_id=user.id,
        token_hash=f"revoked-{uuid4()}",
        expires_at=now + timedelta(days=1),
        revoked_at=now,
    )

    expired_and_revoked_token = RefreshToken(
        user_id=user.id,
        token_hash=f"expired-revoked-{uuid4()}",
        expires_at=now - timedelta(days=1),
        revoked_at=now,
    )

    test_session.add_all(
        [
            active_token,
            expired_token,
            revoked_token,
            expired_and_revoked_token,
        ]
    )

    await test_session.flush()

    deleted_count = await refresh_token_repository.delete_expired_or_revoked()

    await test_session.commit()

    assert deleted_count == 3

    assert await refresh_token_repository.get_by_hash(active_token.token_hash) is not None
    assert await refresh_token_repository.get_by_hash(expired_token.token_hash) is None
    assert await refresh_token_repository.get_by_hash(revoked_token.token_hash) is None
    assert await refresh_token_repository.get_by_hash(expired_and_revoked_token.token_hash) is None


@pytest.mark.asyncio
async def test_revoke_all_for_user(
    test_session: AsyncSession,
    refresh_token_repository: RefreshTokenRepository,
):
    user = await create_test_user(test_session)
    now = datetime.now(UTC)

    token1 = RefreshToken(
        user_id=user.id,
        token_hash=f"t1-{uuid4()}",
        expires_at=now + timedelta(days=1),
        revoked_at=None,
    )
    token2 = RefreshToken(
        user_id=user.id,
        token_hash=f"t2-{uuid4()}",
        expires_at=now + timedelta(days=1),
        revoked_at=None,
    )

    test_session.add_all([token1, token2])
    await test_session.flush()

    await refresh_token_repository.revoke_all_for_user(user.id)

    assert token1.revoked_at is not None
    assert token2.revoked_at is not None
