import pytest
from pydantic import BaseModel, ValidationError

from app.schemas.base import CleanString


class CleanStringTestModel(BaseModel):
    name: CleanString


def test_clean_string_strips_whitespace() -> None:
    result = CleanStringTestModel(name="  Payments Team  ")

    assert result.name == "Payments Team"


def test_clean_string_rejects_empty_string() -> None:
    with pytest.raises(ValidationError):
        CleanStringTestModel(name="")


def test_clean_string_rejects_whitespace_only() -> None:
    with pytest.raises(ValidationError):
        CleanStringTestModel(name="   ")
