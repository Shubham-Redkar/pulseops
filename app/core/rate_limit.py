import hashlib
from uuid import UUID

from .config import settings
from .exceptions import RateLimitExceededError
from .redis import RedisStore


def _hash_identifier(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8"),
    ).hexdigest()


async def _check_rate_limit(
    redis_store: RedisStore,
    *,
    key: str,
    limit: int,
    window: int,
) -> None:
    count = await redis_store.increment(
        key,
        ex=window,
    )

    if count > limit:
        raise RateLimitExceededError()


async def check_alert_rate_limit(
    redis_store: RedisStore,
    user_id: UUID,
) -> None:
    await _check_rate_limit(
        redis_store,
        key=f"rate_limiter:alerts:{user_id}",
        limit=settings.alert_rate_limit,
        window=settings.alert_rate_window,
    )


async def check_login_ip_rate_limit(
    redis_store: RedisStore,
    client_ip: str,
) -> None:
    identifier = _hash_identifier(client_ip)

    await _check_rate_limit(
        redis_store,
        key=f"rate_limiter:login:ip:{identifier}",
        limit=settings.login_rate_limit,
        window=settings.login_rate_window,
    )


async def check_login_username_rate_limit(
    redis_store: RedisStore,
    username: str,
) -> None:
    identifier = _hash_identifier(
        username.strip().lower(),
    )

    await _check_rate_limit(
        redis_store,
        key=f"rate_limiter:login:username:{identifier}",
        limit=settings.login_rate_limit,
        window=settings.login_rate_window,
    )


async def check_refresh_rate_limit(
    redis_store: RedisStore,
    client_ip: str,
) -> None:
    identifier_hash = _hash_identifier(client_ip)

    await _check_rate_limit(
        redis_store,
        key=f"rate_limiter:refresh:{identifier_hash}",
        limit=settings.refresh_rate_limit,
        window=settings.refresh_rate_window,
    )


async def check_forgot_password_rate_limit(
    redis_store: RedisStore,
    client_ip: str,
) -> None:
    identifier_hash = _hash_identifier(client_ip)

    await _check_rate_limit(
        redis_store,
        key=f"rate_limiter:forgot_password:{identifier_hash}",
        limit=settings.forgot_password_rate_limit,
        window=settings.forgot_password_rate_window,
    )


async def check_password_reset_rate_limit(
    redis_store: RedisStore,
    client_ip: str,
) -> None:
    identifier_hash = _hash_identifier(client_ip)

    await _check_rate_limit(
        redis_store,
        key=f"rate_limiter:reset_password:{identifier_hash}",
        limit=settings.forgot_password_rate_limit,
        window=settings.forgot_password_rate_window,
    )


async def check_verify_email_rate_limit(
    redis_store: RedisStore,
    client_ip: str,
) -> None:
    identifier_hash = _hash_identifier(client_ip)

    await _check_rate_limit(
        redis_store,
        key=f"rate_limiter:verify_email:{identifier_hash}",
        limit=settings.email_verification_rate_limit,
        window=settings.email_verification_rate_window,
    )
