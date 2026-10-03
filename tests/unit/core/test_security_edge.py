import jwt
import pytest

from app.core.exceptions import InvalidTokenError
from app.core.security import (
    create_access_token,
    decode_and_validate_access_token,
    hash_email_verification_token,
    hash_password,
    hash_password_reset_token,
    hash_refresh_token,
    verify_password,
    verify_refresh_token,
)

from ...conftest import settings


def test_hash_password_empty() -> None:
    with pytest.raises(ValueError, match="Password must not be empty"):
        hash_password("")


def test_verify_password_empty() -> None:
    assert verify_password("", "hash") is False
    assert verify_password("pass", "") is False


def test_create_access_token_empty() -> None:
    with pytest.raises(ValueError, match="Token subject must not be empty"):
        create_access_token("")


def test_decode_and_validate_access_token_expired() -> None:
    token = jwt.encode(  # type: ignore
        {"exp": 1},
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(InvalidTokenError):
        decode_and_validate_access_token(token)


def test_decode_and_validate_access_token_invalid_signature() -> None:
    token = jwt.encode(  # type: ignore
        {"exp": 9999999999},
        "wrong_secret_that_is_at_least_32_bytes_long",
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(InvalidTokenError):
        decode_and_validate_access_token(token)


def test_decode_and_validate_access_token_malformed_payload() -> None:
    token = jwt.encode(  # type: ignore
        {"sub": 123},
        settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
    with pytest.raises(InvalidTokenError):
        decode_and_validate_access_token(token)


def test_hash_refresh_token_empty() -> None:
    with pytest.raises(ValueError, match="Refresh token must not be empty"):
        hash_refresh_token("")


def test_verify_refresh_token_empty() -> None:
    assert verify_refresh_token("", "hash") is False
    assert verify_refresh_token("token", "") is False


def test_verify_refresh_token_valid() -> None:
    token = "some_token"
    token_hash = hash_refresh_token(token)
    assert verify_refresh_token(token, token_hash) is True


def test_hash_password_reset_token_empty() -> None:
    with pytest.raises(ValueError, match="Password reset token must not be empty"):
        hash_password_reset_token("")


def test_hash_email_verification_token_empty() -> None:
    with pytest.raises(ValueError, match="Email verification token must not be empty"):
        hash_email_verification_token("")
