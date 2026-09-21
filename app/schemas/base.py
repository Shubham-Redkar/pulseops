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
    """
    Provides a UUID identifier field for resource schemas.
    """

    id: UUID = Field(
        examples=["123e4567-e89b-12d3-a456-426614174000"],
        description="Unique identifier for the resource.",
    )


class CreatedAtMixin(BaseModel):
    """
    Provides a timestamp indicating when a resource was created.
    """

    created_at: datetime = Field(
        examples=["2026-01-15T10:30:00Z"],
        description="Timestamp indicating when the resource was created.",
    )


class TimestampMixin(CreatedAtMixin):
    """
    Provides creation and last-update timestamps for resource schemas.
    """

    updated_at: datetime = Field(
        examples=["2026-06-10T08:00:00Z"],
        description="Timestamp indicating when the resource was last updated.",
    )


class PaginatedResponse[T](BaseModel):
    """
    Generic response schema for paginated collections.
    """

    items: list[T]
    limit: int = Field(
        ge=1,
        description="Maximum number of items requested.",
    )
    offset: int = Field(
        ge=0,
        description="Number of items skipped before the current page.",
    )
    total: int = Field(
        ge=0,
        description="Total number of items matching the query.",
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
