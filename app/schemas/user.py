from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from .base import CleanString, IDMixin, ORMBaseSchema, TimestampMixin
from .enums import UserRole


class UserBase(BaseModel):
    """
    Common fields shared by user request and response schemas.
    """

    username: CleanString = Field(
        min_length=3,
        max_length=50,
        description="Username of the user.",
        examples=["john"],
    )

    email: EmailStr = Field(
        max_length=254,
        description="Email address of the user.",
        examples=["john@example.com"],
    )

    role: UserRole = Field(
        description="Role assigned to the user.",
        examples=["admin"],
    )

    team_id: UUID | None = Field(
        default=None,
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
        description="Unique identifier for the team.",
    )


class CreateUserRequest(UserBase):
    """
    Request body for creating a user.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "john",
                "email": "john@example.com",
                "password": "SecurePassword456!",
                "role": "admin",
                "team_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        },
    )

    password: SecretStr = Field(
        min_length=8,
        max_length=128,
        description="Password for the user.",
        examples=["SecurePassword456!"],
    )


class UpdateUserRequest(BaseModel):
    """
    Request body for partially updating a user.
    Only fields provided by the client will be updated.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "john",
                "email": "john@example.com",
                "role": "admin",
                "team_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        },
    )

    username: CleanString | None = Field(
        default=None,
        min_length=3,
        max_length=50,
        description="Username of the user.",
        examples=["john"],
    )

    email: EmailStr | None = Field(
        default=None,
        max_length=254,
        description="Email address of the user.",
        examples=["john@example.com"],
    )

    role: UserRole | None = Field(
        default=None,
        description="Role assigned to the user.",
        examples=["admin"],
    )

    team_id: UUID | None = Field(
        default=None,
        examples=["66dee2d6-f869-4152-9fb9-8461c73506ce"],
        description="Unique identifier for the team.",
    )


class UserResponse(
    ORMBaseSchema,
    IDMixin,
    TimestampMixin,
    UserBase,
):
    """
    Response representation of a user.
    """
