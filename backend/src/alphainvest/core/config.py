from functools import lru_cache
from typing import Literal, Self
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import (
    Field,
    PostgresDsn,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

DatabaseSslMode = Literal[
    "disable",
    "require",
    "verify-ca",
    "verify-full",
]

JwtAlgorithm = Literal["HS256"]


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
    version: str = "1.0.0"
    env: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    cors_origins: list[str] = Field(
        default_factory=list,
    )

    database_url: PostgresDsn = PostgresDsn(
        "postgresql+asyncpg://"
        "postgres:postgres@localhost:5432/"
        "alphainvest_db"
    )
    database_echo: bool = False
    database_pool_size: int = Field(
        default=5,
        ge=1,
    )
    database_max_overflow: int = Field(
        default=10,
        ge=0,
    )
    database_pool_timeout: int = Field(
        default=30,
        ge=1,
    )
    database_pool_recycle: int = Field(
        default=1800,
        ge=60,
    )
    database_command_timeout: int = Field(
        default=10,
        ge=1,
    )
    database_ssl_mode: DatabaseSslMode = "disable"
    database_ssl_ca_file: str | None = None

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "alphainvest_documents"
    mongodb_news_collection: str = "noticias"
    mongodb_server_selection_timeout_ms: int = Field(
        default=5000,
        ge=100,
        le=60000,
    )

    jwt_secret_key: str = (
        "CHANGE_ME_IN_PRODUCTION_WITH_AT_LEAST_32_CHARACTERS"
    )
    jwt_algorithm: JwtAlgorithm = "HS256"
    access_token_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
    )
    refresh_token_days: int = Field(
        default=30,
        ge=1,
        le=365,
    )
    max_failed_login_attempts: int = Field(
        default=5,
        ge=1,
        le=20,
    )
    login_lock_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,
    )
    default_role: str = "INVERSIONISTA"

    alpha_vantage_api_key: str | None = None
    alpha_vantage_base_url: str = (
        "https://www.alphavantage.co"
    )
    alpha_vantage_timeout_seconds: float = Field(
        default=15.0,
        gt=0,
        le=120,
    )
    alpha_vantage_output_size: str = "compact"

    worker_enabled: bool = False
    worker_run_on_startup: bool = False
    worker_run_once: bool = False
    worker_run_once_job: str = (
        "ACTUALIZAR_PRECIOS_DIARIOS"
    )
    worker_timezone: str = "America/Mexico_City"
    worker_price_sync_symbols: str = "AAPL"
    worker_simulation_source_name: str = (
        "Alpha Vantage"
    )
    worker_simulation_batch_size: int = Field(
        default=10,
        ge=1,
        le=100,
    )
    worker_ai_analysis_source_name: str = (
        "Yahoo Finance"
    )
    worker_ai_analysis_batch_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )
    worker_ai_analysis_lock_seconds: int = Field(
        default=1800,
        ge=60,
        le=86400,
    )
    worker_max_instances: int = Field(
        default=1,
        ge=1,
        le=10,
    )
    worker_misfire_grace_seconds: int = Field(
        default=300,
        ge=0,
        le=86400,
    )

    @field_validator("database_url")
    @classmethod
    def validate_async_driver(
        cls,
        value: PostgresDsn,
    ) -> PostgresDsn:
        if value.scheme != "postgresql+asyncpg":
            raise ValueError(
                "APP_DATABASE_URL debe usar "
                "postgresql+asyncpg"
            )

        return value

    @field_validator("database_ssl_ca_file")
    @classmethod
    def normalize_database_ssl_ca_file(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()

        return normalized or None

    @field_validator("alpha_vantage_output_size")
    @classmethod
    def validate_alpha_vantage_output_size(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip().lower()

        if normalized not in {
            "compact",
            "full",
        }:
            raise ValueError(
                "APP_ALPHA_VANTAGE_OUTPUT_SIZE debe ser "
                "'compact' o 'full'"
            )

        return normalized

    @model_validator(mode="after")
    def validate_production_security(
        self,
    ) -> Self:
        environment = self.env.strip().lower()

        if environment not in {
            "production",
            "prod",
        }:
            return self

        if self.debug:
            raise ValueError(
                "APP_DEBUG debe ser false en producción"
            )

        jwt_secret = self.jwt_secret_key.strip()

        insecure_jwt_values = {
            "CHANGE_ME_IN_PRODUCTION_WITH_AT_LEAST_32_CHARACTERS",
            "CAMBIA_ESTA_CLAVE_POR_UNA_DE_AL_MENOS_32_CARACTERES",
        }

        if (
            len(jwt_secret) < 32
            or jwt_secret in insecure_jwt_values
        ):
            raise ValueError(
                "APP_JWT_SECRET_KEY debe contener una "
                "clave segura de al menos 32 caracteres "
                "en producción"
            )

        database_url = self.database_url_string.lower()

        insecure_database_patterns = (
            "postgres:postgres@localhost",
            "postgres:postgres@127.0.0.1",
            "postgres:cambia_esta_clave@localhost",
            "postgres:cambia_esta_clave@127.0.0.1",
        )

        if any(
            pattern in database_url
            for pattern in insecure_database_patterns
        ):
            raise ValueError(
                "APP_DATABASE_URL utiliza credenciales "
                "inseguras para producción"
            )

        if self.database_ssl_mode == "disable":
            raise ValueError(
                "APP_DATABASE_SSL_MODE no puede ser "
                "'disable' en producción"
            )

        if "*" in self.cors_origins:
            raise ValueError(
                "APP_CORS_ORIGINS no puede contener '*' "
                "en producción"
            )

        return self

    @property
    def database_url_string(self) -> str:
        return str(self.database_url)

    @property
    def alembic_database_url(self) -> str:
        """Convierte asyncpg a psycopg y agrega configuración SSL."""

        database_url = self.database_url_string.replace(
            "postgresql+asyncpg",
            "postgresql+psycopg",
            1,
        )

        parsed = urlsplit(database_url)
        query = dict(
            parse_qsl(
                parsed.query,
                keep_blank_values=True,
            )
        )

        query["sslmode"] = self.database_ssl_mode

        if self.database_ssl_ca_file is not None:
            query["sslrootcert"] = self.database_ssl_ca_file

        return urlunsplit(
            (
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                urlencode(query),
                parsed.fragment,
            )
        )

    @property
    def worker_price_symbols(self) -> list[str]:
        return [
            symbol.strip().upper()
            for symbol
            in self.worker_price_sync_symbols.split(",")
            if symbol.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
