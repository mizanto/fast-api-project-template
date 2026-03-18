from functools import lru_cache

from typing import ClassVar

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application name will appear in Swagger/OpenAPI
    app_name: str = (
        "Template FastAPI Project"  # TODO: Change this to the name of your project
    )

    # Flag debug is useful for logs and SQLAlchemy echo
    debug: bool = False

    # Logging verbosity (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    log_level: str = "INFO"

    cors_allowed_origins: list[str] = ["*"]

    VALID_LOG_LEVELS: ClassVar[set[str]] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, v: str) -> str:
        upper = v.upper()
        if upper not in cls.VALID_LOG_LEVELS:
            raise ValueError(
                f"Invalid log_level '{v}'. Must be one of: {sorted(cls.VALID_LOG_LEVELS)}"
            )
        return upper

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_allowed_origins(cls, v):
        # Support common env formats:
        # - CORS_ALLOWED_ORIGINS=* (single wildcard)
        # - CORS_ALLOWED_ORIGINS=    (empty/whitespace) -> treated as "*"
        # - CORS_ALLOWED_ORIGINS=https://a.com,https://b.com (comma-separated)
        # - CORS_ALLOWED_ORIGINS='["https://a.com","https://b.com"]' (JSON list)
        if v is None:
            return ["*"]
        if isinstance(v, str):
            raw = v.strip()
            if not raw:
                # Empty string behaves like wildcard for convenience.
                return ["*"]
            if raw == "*":
                return ["*"]
            return [part.strip() for part in raw.split(",") if part.strip()]
        return v

    # API prefix, to get used to versioning right away
    api_v1_prefix: str = "/api/v1"

    # For now SQLite, later we can replace it with PostgreSQL without rewriting the code.
    #
    # SQLite (async):      sqlite+aiosqlite:///./app.db  (requires `aiosqlite`)
    # PostgreSQL (async):  postgresql+asyncpg://user:pass@host:5432/dbname  (requires `asyncpg`)
    database_url: str = (
        "sqlite+aiosqlite:///./app.db"  # TODO: Change this to the database URL of your project
    )

    # Tell pydantic-settings to read variables from .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# lru_cache is needed to prevent Settings from being created again when imported
@lru_cache
def get_settings() -> Settings:
    return Settings()
