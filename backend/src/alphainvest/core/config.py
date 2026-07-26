from functools import lru_cache

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central cargada desde variables APP_* y archivo .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

    name: str = "AlphaInvest AI API"
    version: str = "0.3.0"
    env: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(default_factory=list)

    database_url: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/alphainvest_db"
    )
    database_echo: bool = False
    database_pool_size: int = Field(default=5, ge=1)
    database_max_overflow: int = Field(default=10, ge=0)
    database_pool_timeout: int = Field(default=30, ge=1)
    database_pool_recycle: int = Field(default=1800, ge=60)
    database_command_timeout: int = Field(default=10, ge=1)

    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION_WITH_AT_LEAST_32_CHARACTERS"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = Field(default=15, ge=1, le=1440)
    refresh_token_days: int = Field(default=30, ge=1, le=365)
    max_failed_login_attempts: int = Field(default=5, ge=1, le=20)
    login_lock_minutes: int = Field(default=15, ge=1, le=1440)
    default_role: str = "INVERSIONISTA"

    @field_validator("database_url")
    @classmethod
    def validate_async_driver(cls, value: PostgresDsn) -> PostgresDsn:
        if value.scheme != "postgresql+asyncpg":
            raise ValueError("APP_DATABASE_URL debe usar postgresql+asyncpg")
        return value

    @property
    def database_url_string(self) -> str:
        return str(self.database_url)

    @property
    def alembic_database_url(self) -> str:
        """Alembic usa un driver síncrono solo para ejecutar comandos de migración."""
        return self.database_url_string.replace("postgresql+asyncpg", "postgresql+psycopg")


@lru_cache
def get_settings() -> Settings:
    return Settings()
