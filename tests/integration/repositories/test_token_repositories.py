import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.models.email_verification_token import EmailVerificationToken
from app.db.models.idempotency_key import IdempotencyKey
from app.db.models.password_reset_token import PasswordResetToken
from app.db.models.user import User
from app.repositories.email_verification_token_repository import EmailVerificationTokenRepository
from app.repositories.idempotency_repository import IdempotencyRepository
from app.repositories.password_reset_token_repository import PasswordResetTokenRepository
from app.schemas.enums import UserRole


async def create_mock_user(
    session: AsyncSession,
) -> User:
    user = User(
        id=uuid.uuid4(),
        first_name="Test",
        last_name="User",
        username=f"testuser_{uuid.uuid4()}",
        email=f"test_{uuid.uuid4()}@example.com",
        password_hash=hash_password("password"),
        role=UserRole.VIEWER,
        email_verified=True,
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return user


@pytest.mark.asyncio
async def test_email_verification_repo_create_and_get(
    test_session: AsyncSession,
) -> None:
    user = await create_mock_user(test_session)
    repo = EmailVerificationTokenRepository(test_session)

    token = EmailVerificationToken(
        user_id=user.id,
        token_hash="hash1",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )

    saved_token = await repo.create(token)
    assert saved_token.id is not None

    found_token = await repo.get_by_hash("hash1")
    assert found_token is not None
    assert found_token.id == saved_token.id


@pytest.mark.asyncio
async def test_email_verification_repo_invalidate(
    test_session: AsyncSession,
) -> None:
    user = await create_mock_user(test_session)
    repo = EmailVerificationTokenRepository(test_session)

    token = EmailVerificationToken(
        user_id=user.id,
        token_hash="hash2",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    await repo.create(token)

    await repo.invalidate_unused_for_user(user.id)
    await test_session.commit()

    found_token = await repo.get_by_hash("hash2")
    assert found_token is not None
    assert found_token.used_at is not None


@pytest.mark.asyncio
async def test_password_reset_repo_create_and_get(
    test_session: AsyncSession,
) -> None:
    user = await create_mock_user(test_session)
    repo = PasswordResetTokenRepository(test_session)

    token = PasswordResetToken(
        user_id=user.id,
        token_hash="hash_pr1",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )

    saved_token = await repo.create(token)
    assert saved_token.id is not None

    found_token = await repo.get_by_hash("hash_pr1")
    assert found_token is not None
    assert found_token.id == saved_token.id


@pytest.mark.asyncio
async def test_password_reset_repo_invalidate(
    test_session: AsyncSession,
) -> None:
    user = await create_mock_user(test_session)
    repo = PasswordResetTokenRepository(test_session)

    token = PasswordResetToken(
        user_id=user.id,
        token_hash="hash_pr2",
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
    )
    await repo.create(token)

    await repo.invalidate_unused_for_user(user.id)
    await test_session.commit()

    found_token = await repo.get_by_hash("hash_pr2")
    assert found_token is not None
    assert found_token.used_at is not None


@pytest.mark.asyncio
async def test_idempotency_repo(
    test_session: AsyncSession,
) -> None:
    from app.repositories.alert_repository import AlertRepository
    from tests.integration.repositories.test_alert_repository import (
        create_mock_alert,
        create_mock_service,
    )

    service = await create_mock_service(test_session)
    alert = create_mock_alert(service.id)
    alert_repo = AlertRepository(test_session)
    await alert_repo.create(alert)

    repo = IdempotencyRepository(test_session)
    key = IdempotencyKey(key="idemp_key_1", alert_id=alert.id)

    saved_key = await repo.create(key)
    assert saved_key.id is not None

    found_key = await repo.get_by_key("idemp_key_1")
    assert found_key is not None
    assert found_key.alert_id == alert.id
