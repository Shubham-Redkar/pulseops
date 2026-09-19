from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .enums import ErrorCode


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "code": "NOT_FOUND",
                "message": "Resource was not found.",
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        },
    )

    code: ErrorCode = Field(
        description="Machine-readable error code.",
        examples=[ErrorCode.NOT_FOUND],
    )

    message: str = Field(
        min_length=1,
        max_length=500,
        description="Human-readable description of the error.",
        examples=["Resource was not found."],
    )

    request_id: UUID | None = Field(
        default=None,
        description="Unique identifier for tracing the request.",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )
