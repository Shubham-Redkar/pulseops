from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

    redis_url: str

    secret_key: SecretStr = Field(min_length=32)

    jwt_algorithm: Literal["HS256", "HS384", "HS512"]

    access_token_expire_minutes: int = Field(
        ge=1,
        le=60,
    )

    refresh_token_expire_days: int = Field(
        ge=1,
        le=365,
    )

    password_reset_token_expire_minutes: int = Field(
        ge=1,
        le=60,
    )

    email_verification_token_expire_minutes: int = Field(
        ge=1,
        le=60,
    )

    account_lockout_minutes: int = Field(
        ge=1,
        le=30,
    )

    account_login_attempts: int = Field(
        ge=1,
        le=10,
    )

    alert_rate_limit: int = Field(
        ge=100,
        le=1000,
    )

    alert_rate_window: int = Field(
        ge=60,
        le=120,
    )

    login_rate_limit: int = Field(
        ge=1,
        le=10,
    )

    login_rate_window: int = Field(
        ge=60,
        le=120,
    )

    refresh_rate_limit: int = Field(
        ge=1,
        le=20,
    )

    refresh_rate_window: int = Field(
        ge=60,
        le=120,
    )

    forgot_password_rate_limit: int = Field(
        ge=1,
        le=6,
    )

    forgot_password_rate_window: int = Field(
        ge=300,
        le=600,
    )

    email_verification_rate_limit: int = Field(
        ge=1,
        le=20,
    )

    email_verification_rate_window: int = Field(
        60,
        le=600,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("DATABASE_URL must not be empty.")
        return value

    @field_validator("redis_url")
    @classmethod
    def validate_redis_url(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("REDIS_URL must not be empty.")
        return value


settings = Settings()  # type: ignore
