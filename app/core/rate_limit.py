from uuid import UUID

from .config import settings
from .exceptions import RateLimitExceededError
from .redis import RedisStore


async def check_alert_rate_limit(
    redis_store: RedisStore,
    user_id: UUID,
) -> None:
    key = f"rate_limiter:alerts:{user_id}"

    count = await redis_store.increment(
        key,
        ex=settings.alert_rate_window,
    )

    if count > settings.alert_rate_limit:
        raise RateLimitExceededError()


async def check_login_ip_rate_limit(
    redis_store: RedisStore,
    client_ip: str,
) -> None:
    key = f"rate_limiter:login:ip:{client_ip}"

    count = await redis_store.increment(
        key,
        ex=settings.login_rate_window,
    )

    if count > settings.login_rate_limit:
        raise RateLimitExceededError()


async def check_login_username_rate_limit(
    redis_store: RedisStore,
    username: str,
) -> None:
    key = f"rate_limiter:login:username:{username}"

    count = await redis_store.increment(
        key,
        ex=settings.login_rate_window,
    )

    if count > settings.login_rate_limit:
        raise RateLimitExceededError()


async def check_refresh_rate_limit(
    redis_store: RedisStore,
    identifier: str,
) -> None:
    key = f"rate_limiter:refresh:{identifier}"

    count = await redis_store.increment(
        key,
        ex=settings.refresh_rate_window,
    )

    if count > settings.refresh_rate_limit:
        raise RateLimitExceededError()


async def check_forgot_password_rate_limit(
    redis_store: RedisStore,
    identifier: str,
) -> None:
    key = f"rate_limiter:forgot_password:{identifier}"

    count = await redis_store.increment(
        key,
        ex=settings.forgot_password_rate_window,
    )

    if count > settings.forgot_password_rate_limit:
        raise RateLimitExceededError()


async def check_password_reset_rate_limit(
    redis_store: RedisStore,
    identifier: str,
) -> None:
    key = f"rate_limiter:reset_password:{identifier}"

    count = await redis_store.increment(
        key,
        ex=settings.forgot_password_rate_window,
    )

    if count > settings.forgot_password_rate_limit:
        raise RateLimitExceededError()


async def check_verify_email_rate_limit(
    redis_store: RedisStore,
    identifier: str,
) -> None:
    key = f"rate_limiter:verify_email:{identifier}"

    count = await redis_store.increment(
        key,
        ex=settings.email_verification_rate_window,
    )

    if count > settings.email_verification_rate_limit:
        raise RateLimitExceededError()
