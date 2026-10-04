from typing import cast

from redis import RedisError
from redis.asyncio import Redis

from .config import settings
from .exceptions import ServiceUnavailableError

redis_client = Redis.from_url(  # pyright: ignore[reportUnknownMemberType]
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2,
    health_check_interval=30,
)


class RedisStore:
    """
    Application-level abstraction over Redis.

    Responsibilities:
    - Simple key/value operations.
    - Atomic counters.
    - Cache-aside support.
    - Distributed lock primitives.

    Redis connection lifecycle is managed by the application.
    """

    _INCREMENT_WITH_EXPIRY_SCRIPT = """
    local count = redis.call("INCR", KEYS[1])

    if count == 1 then
        redis.call("EXPIRE", KEYS[1], ARGV[1])
    end

    return count
    """

    _RELEASE_LOCK_SCRIPT = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    end
    return 0
    """

    def __init__(
        self,
        client: Redis,
    ) -> None:
        self._client = client

    async def get(self, key: str) -> str | None:
        value = await self._client.get(key)

        return cast(str | None, value)

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
    ) -> bool:
        self._validate_expiry(ex)

        result = await self._client.set(
            key,
            value,
            ex=ex,
        )

        return bool(result)

    async def delete(
        self,
        key: str,
    ) -> bool:
        deleted = await self._client.delete(key)

        return bool(deleted)

    async def increment(
        self,
        key: str,
        *,
        ex: int | None = None,
    ) -> int:
        self._validate_expiry(ex)

        if ex is None:
            return int(await self._client.incr(key))

        result = await self._client.eval(
            self._INCREMENT_WITH_EXPIRY_SCRIPT,
            1,
            key,
            ex,
        )

        return int(result)

    async def acquire_lock(
        self,
        key: str,
        token: str,
        *,
        ex: int,
    ) -> bool:
        self._validate_expiry(ex)

        result = await self._client.set(
            key,
            token,
            nx=True,
            ex=ex,
        )

        return bool(result)

    async def release_lock(
        self,
        key: str,
        token: str,
    ) -> bool:
        result = await self._client.eval(
            self._RELEASE_LOCK_SCRIPT,
            1,
            key,
            token,
        )

        return bool(result)

    async def ping(self) -> bool:
        try:
            return bool(await self._client.ping())  # pyright: ignore[reportUnknownMemberType]
        except RedisError as exc:
            raise ServiceUnavailableError(
                "Redis is not ready.",
            ) from exc

    async def close(self) -> None:
        await self._client.aclose()

    @staticmethod
    def _validate_expiry(ex: int | None) -> None:
        if ex is not None and ex <= 0:
            raise ValueError("ex must be greater than 0")


redis_store = RedisStore(redis_client)
