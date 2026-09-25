from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str

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


settings = Settings()  # type: ignore
