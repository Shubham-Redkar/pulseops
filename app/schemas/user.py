from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .base import IDMixin, ORMBaseSchema, TimeStampMixin
from .enums import UserRole


class UserBase(BaseModel):
    """
    Common fields shared by user request and response schemas.
    """

    username: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Username of the user.",
        examples=["john"],
    )

    email: EmailStr = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Email address of the user.",
        examples=["john@example.com"],
    )

    role: UserRole = Field(
        ...,
        description="Role assigned to the user.",
        examples=["admin"],
    )


class CreateUserRequest(UserBase):
    """
    Request body for creating an user.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "john",
                "email": "john@example.com",
                "password": "SecurePassword456!",
                "role": "admin",
            }
        },
    )

    password: str = Field(
        ...,
        min_length=8,
        description="Password for the user.",
        examples=["SecurePassword456!"],
    )


class UpdateUserRequest(BaseModel):
    """
    Request body for partially updating an user.
    Only fields provided by the client will be updated.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "username": "john",
                "email": "john@example.com",
                "role": "admin",
            }
        },
    )

    username: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Username of the user.",
        examples=["john"],
    )

    email: EmailStr | None = Field(
        default=None,
        min_length=1,
        max_length=5000,
        description="Email address of the user.",
        examples=["john@example.com"],
    )

    role: UserRole | None = Field(
        default=None,
        description="Role assigned to the user.",
        examples=["admin"],
    )


class UserResponse(
    ORMBaseSchema,
    IDMixin,
    TimeStampMixin,
    UserBase,
):
    """
    Response representation of an user.
    """
