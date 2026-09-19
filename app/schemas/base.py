from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


class ORMBaseSchema(BaseModel):
    """
    Base schema configured for ORM model serialization.
    """

    model_config = ConfigDict(from_attributes=True)


class IDMixin(BaseModel):
    id: UUID = Field(
        ...,
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        description="Unique identifier for the resource.",
    )


class CreatedAtMixin(BaseModel):
    created_at: datetime = Field(
        ...,
        examples=["2026-01-15T10:30:00Z"],
        description="Timestamp indicating when the resource was created.",
    )


class TimeStampMixin(CreatedAtMixin):
    updated_at: datetime = Field(
        examples=["2026-06-10T08:00:00Z"],
        description="Timestamp indicating when the resource was last updated.",
    )


def strip_and_validate_string(value: str) -> str:
    """
    Strip leading/trailing whitespace and reject empty/whitespace-only strings.
    """
    value = value.strip()

    if not value:
        raise ValueError("Must not be empty or whitespace")

    return value


CleanString = Annotated[str, AfterValidator(strip_and_validate_string)]
