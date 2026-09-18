from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    updated_at: datetime | None = Field(
        default=None,
        examples=["2026-06-10T08:00:00Z"],
        description="Timestamp indicating when the resource was last updated.",
    )
