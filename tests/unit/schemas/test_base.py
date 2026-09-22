import pytest

from app.schemas.base import strip_and_validate_string


def test_strip_and_validate_string_rejects_whitespace() -> None:
    with pytest.raises(
        ValueError,
        match="Must not be empty or whitespace",
    ):
        strip_and_validate_string("   ")


def test_strip_and_validate_string_strips_whitespace() -> None:
    assert strip_and_validate_string("  Payments Team  ") == "Payments Team"
