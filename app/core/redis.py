from typing import cast

from redis.asyncio import Redis

from .config import settings

redis_client = Redis.from_url(  # pyright: ignore[reportUnknownMemberType]
    settings.redis_url,
    encoding="utf-8",
    decode_responses=True,
)


class RedisStore:
    """
    Small abstraction over the shared Redis client.
    """

    def __init__(
        self,
        client: Redis,
    ) -> None:
        self.client = client

    async def get(self, key: str) -> str | None:
        value = await self.client.get(key)

        return cast(str | None, value)

    async def set(
        self,
        key: str,
        value: str,
        *,
        ex: int | None = None,
    ) -> bool:
        result = await self.client.set(
            key,
            value,
            ex=ex,
        )

        return cast(bool, result)

    async def delete(
        self,
        key: str,
    ) -> int:
        return await self.client.delete(key)
