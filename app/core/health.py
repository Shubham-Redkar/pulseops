from redis.exceptions import RedisError

from .exceptions import ServiceUnavailableError
from .redis import redis_client


async def check_redis() -> None:
    """
    Check whether Redis is reachable.
    """
    try:
        await redis_client.ping()  # pyright: ignore[reportUnknownMemberType]
    except RedisError as exc:
        raise ServiceUnavailableError("Redis is not ready.") from exc
