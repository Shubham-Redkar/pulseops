from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..core.errors import ErrorCode
from .base import CleanString


class ErrorDetail(BaseModel):
    """
    Individual validation error detail.
    """

    field: str = Field(
        min_length=1,
        max_length=255,
        description="Field associated with the error.",
        examples=["email"],
    )

    message: CleanString = Field(
        max_length=500,
        description="Description of the validation error.",
        examples=["Invalid email address."],
    )


class ErrorResponse(BaseModel):
    """
    Standard API error response.
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    code: ErrorCode = Field(
        description="Machine-readable error code.",
        examples=["NOT_FOUND"],
    )

    message: CleanString = Field(
        max_length=500,
        description="Human-readable description of the error.",
        examples=["Resource was not found."],
    )

    request_id: UUID = Field(
        description="Unique identifier for tracing the request.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    details: list[ErrorDetail] | None = Field(
        default=None,
        description="Additional details about the error.",
    )
