from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
    field_validator,
)

from app.schemas.base import CleanString

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_.-]+$",
    ),
]

Password = Annotated[
    SecretStr,
    Field(
        min_length=8,
        max_length=128,
        description="User password.",
        repr=False,
    ),
]

Name = Annotated[
    CleanString,
    StringConstraints(
        min_length=1,
        max_length=100,
    ),
]


class RequestModel(BaseModel):
    """
    Base model for inbound API payloads.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class RegisterRequest(RequestModel):
    """
    Payload used to create a new user account.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "username": "john_doe",
                "email": "john@example.com",
                "password": "StrongPassword123!",
            }
        },
    )

    first_name: Name = Field(
        description="User's first name.",
        examples=["John"],
    )

    last_name: Name = Field(
        description="User's last name.",
        examples=["Doe"],
    )

    username: Username = Field(
        description="Unique username.",
        examples=["john_doe"],
    )

    email: EmailStr = Field(
        description="User's email address.",
        examples=["john@example.com"],
    )

    password: Password

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.lower()

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class LoginRequest(RequestModel):
    """
    Payload used to authenticate an existing user.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "StrongPassword123!",
            }
        },
    )

    username: Username = Field(
        description="Username used for authentication.",
        examples=["john_doe"],
    )

    password: Password

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.lower()


class ChangePasswordRequest(RequestModel):
    """
    Payload used to change the authenticated user's password.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewPassword123!",
            }
        },
    )

    current_password: Password

    new_password: Password


class RefreshTokenRequest(RequestModel):
    """
    Payload used to request a new access token.
    """

    model_config = ConfigDict(
        json_schema_extra={"example": {"refresh_token": "dBjftJeZ4CVP-mB92K27uhbU..."}},
    )

    refresh_token: SecretStr = Field(
        min_length=1,
        description="Refresh token used to obtain a new access token.",
    )


class ForgotPasswordRequest(RequestModel):
    """
    Payload used to request a password reset.
    """

    email: EmailStr = Field(
        description="User's email address.",
        examples=["john@example.com"],
    )

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).lower()


class ResetPasswordRequest(RequestModel):
    """
    Payload used to reset a user's password using a password reset token.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "reset_token": "dBjftJeZ4CVP-mB92K27uhbU...",
                "new_password": "NewStrongPassword123!",
            }
        },
    )

    reset_token: SecretStr = Field(
        min_length=1,
        description="Password reset token.",
    )

    new_password: Password


class VerifyEmailRequest(RequestModel):
    """
    Payload used to verify a user's email address.
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "dBjftJeZ4CVP-mB92K27uhbU...",
            }
        },
    )

    token: SecretStr = Field(
        min_length=1,
        description="Email verification token.",
    )


class TokenResponse(BaseModel):
    """
    Authentication tokens returned after successful login.
    """

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900,
                "refresh_token": "dBjftJeZ4CVP-mB92K27uhbU...",
                "refresh_expires_in": 604800,
            }
        },
    )

    access_token: str = Field(
        min_length=1,
        description="Short-lived access token.",
    )

    token_type: Literal["bearer"] = Field(
        default="bearer",
        description="Authentication scheme.",
    )

    expires_in: int = Field(
        gt=0,
        description="Access token lifetime in seconds.",
        examples=[900],
    )

    refresh_token: str = Field(
        min_length=1,
        description="Long-lived token used to obtain a new access token.",
    )

    refresh_expires_in: int = Field(
        gt=0,
        description="Refresh token lifetime in seconds.",
        examples=[604800],
    )
