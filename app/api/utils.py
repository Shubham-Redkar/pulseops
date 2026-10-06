from fastapi import Response


def set_rate_limit_headers(
    response: Response,
    *,
    limit: int,
    remaining: int,
    reset: int,
) -> None:
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset)
