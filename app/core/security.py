import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import TypedDict
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from .config import settings
from .exceptions import InvalidTokenError


class AccessTokenPayload(TypedDict):
    sub: str
    type: str
    iat: int
    exp: int
    jti: str


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Generate a secure password hash."""
    if not password:
        raise ValueError("Password must not be empty.")

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its stored hash."""
    if not password or not password_hash:
        return False

    return password_hasher.verify(password, password_hash)


def create_access_token(subject: str) -> str:
    """Create a signed JWT access token."""
    if not subject:
        raise ValueError("Token subject must not be empty.")

    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        "sub": subject,
        "type": "access",
        "iat": now,
        "exp": expires_at,
        "jti": str(uuid4()),
    }

    return jwt.encode(  # type: ignore[reportUnknownMemberType]
        payload=payload,
        key=settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_and_validate_access_token(token: str) -> AccessTokenPayload:
    """Decode and validate an access token."""
    try:
        payload = jwt.decode(  # type: ignore[reportUnknownMemberType]
            jwt=token,
            key=settings.secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise InvalidTokenError() from exc
    except jwt.InvalidTokenError as exc:
        raise InvalidTokenError() from exc

    subject = payload.get("sub")
    token_type = payload.get("type")
    issued_at = payload.get("iat")
    expires_at = payload.get("exp")
    token_id = payload.get("jti")

    if (
        not isinstance(subject, str)
        or not subject
        or token_type != "access"
        or not isinstance(issued_at, int)
        or not isinstance(expires_at, int)
        or not isinstance(token_id, str)
    ):
        raise InvalidTokenError()

    return {
        "sub": subject,
        "type": token_type,
        "iat": issued_at,
        "exp": expires_at,
        "jti": token_id,
    }


def generate_refresh_token() -> str:
    """Generate a cryptographically secure opaque refresh token."""
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    """Hash an opaque refresh token for database storage."""
    if not token:
        raise ValueError("Refresh token must not be empty.")

    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_refresh_token(token: str, token_hash: str) -> bool:
    """Verify an opaque refresh token against its stored hash."""
    if not token or not token_hash:
        return False

    expected_hash = hash_refresh_token(token)

    return secrets.compare_digest(expected_hash, token_hash)
