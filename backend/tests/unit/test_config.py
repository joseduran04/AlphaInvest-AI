import pytest
from pydantic import ValidationError

from alphainvest.core.config import Settings


@pytest.mark.unit
def test_default_settings() -> None:
    settings = Settings(
        _env_file=None,
    )

    assert settings.name == "AlphaInvest AI API"
    assert settings.version == "1.0.0"
    assert settings.env == "local"
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.log_level == "INFO"

    assert settings.database_ssl_mode == "disable"
    assert settings.database_ssl_ca_file is None

    assert (
        settings.mongodb_uri
        == "mongodb://localhost:27017"
    )

    assert (
        settings.mongodb_database
        == "alphainvest_documents"
    )

    assert (
        settings.mongodb_news_collection
        == "noticias"
    )

    assert (
        settings.mongodb_server_selection_timeout_ms
        == 5000
    )

    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_minutes == 15
    assert settings.refresh_token_days == 30
    assert settings.max_failed_login_attempts == 5
    assert settings.login_lock_minutes == 15
    assert settings.default_role == "INVERSIONISTA"

    assert settings.alpha_vantage_api_key is None
    assert (
        settings.alpha_vantage_base_url
        == "https://www.alphavantage.co"
    )
    assert (
        settings.alpha_vantage_timeout_seconds
        == 15.0
    )
    assert (
        settings.alpha_vantage_output_size
        == "compact"
    )

    assert settings.worker_enabled is False
    assert settings.worker_run_on_startup is False
    assert settings.worker_run_once is False

    assert (
        settings.worker_timezone
        == "America/Mexico_City"
    )

    assert settings.worker_price_symbols == [
        "AAPL",
    ]

    assert settings.worker_max_instances == 1

    assert (
        settings.worker_misfire_grace_seconds
        == 300
    )

    assert (
        settings.worker_run_once_job
        == "ACTUALIZAR_PRECIOS_DIARIOS"
    )


@pytest.mark.unit
def test_worker_simulation_defaults() -> None:
    settings = Settings(
        _env_file=None,
        database_url=(
            "postgresql+asyncpg://"
            "user:password@localhost/test"
        ),
    )

    assert (
        settings.worker_simulation_source_name
        == "Alpha Vantage"
    )

    assert (
        settings.worker_simulation_batch_size
        == 10
    )


@pytest.mark.unit
def test_ai_worker_defaults() -> None:
    settings = Settings(
        _env_file=None,
    )

    assert (
        settings.worker_ai_analysis_source_name
        == "Yahoo Finance"
    )

    assert (
        settings.worker_ai_analysis_batch_size
        == 20
    )

    assert (
        settings.worker_ai_analysis_lock_seconds
        == 1800
    )


@pytest.mark.unit
def test_production_accepts_secure_configuration() -> None:
    settings = Settings(
        _env_file=None,
        env="production",
        debug=False,
        database_url=(
            "postgresql+asyncpg://"
            "alphainvest:secure-password@"
            "db.example.com:5432/alphainvest"
        ),
        database_ssl_mode="require",
        jwt_secret_key=(
            "a-very-long-production-secret-key-"
            "for-alphainvest"
        ),
        cors_origins=[
            "https://app.example.com",
        ],
    )

    assert settings.env == "production"
    assert settings.debug is False
    assert settings.database_ssl_mode == "require"


@pytest.mark.unit
def test_production_rejects_debug_enabled() -> None:
    with pytest.raises(
        ValidationError,
        match="APP_DEBUG debe ser false",
    ):
        Settings(
            _env_file=None,
            env="production",
            debug=True,
            database_url=(
                "postgresql+asyncpg://"
                "alphainvest:secure-password@"
                "db.example.com:5432/alphainvest"
            ),
            database_ssl_mode="require",
            jwt_secret_key=(
                "a-very-long-production-secret-key-"
                "for-alphainvest"
            ),
        )


@pytest.mark.unit
def test_production_rejects_default_jwt_secret() -> None:
    with pytest.raises(
        ValidationError,
        match="APP_JWT_SECRET_KEY",
    ):
        Settings(
            _env_file=None,
            env="production",
            debug=False,
            database_url=(
                "postgresql+asyncpg://"
                "alphainvest:secure-password@"
                "db.example.com:5432/alphainvest"
            ),
            database_ssl_mode="require",
        )


@pytest.mark.unit
def test_production_rejects_short_jwt_secret() -> None:
    with pytest.raises(
        ValidationError,
        match="APP_JWT_SECRET_KEY",
    ):
        Settings(
            _env_file=None,
            env="production",
            debug=False,
            database_url=(
                "postgresql+asyncpg://"
                "alphainvest:secure-password@"
                "db.example.com:5432/alphainvest"
            ),
            database_ssl_mode="require",
            jwt_secret_key="short-secret",
        )


@pytest.mark.unit
def test_production_rejects_insecure_database_credentials() -> None:
    with pytest.raises(
        ValidationError,
        match="APP_DATABASE_URL",
    ):
        Settings(
            _env_file=None,
            env="production",
            debug=False,
            database_url=(
                "postgresql+asyncpg://"
                "postgres:postgres@localhost:5432/"
                "alphainvest_db"
            ),
            database_ssl_mode="require",
            jwt_secret_key=(
                "a-very-long-production-secret-key-"
                "for-alphainvest"
            ),
        )


@pytest.mark.unit
def test_production_rejects_database_ssl_disabled() -> None:
    with pytest.raises(
        ValidationError,
        match="APP_DATABASE_SSL_MODE",
    ):
        Settings(
            _env_file=None,
            env="production",
            debug=False,
            database_url=(
                "postgresql+asyncpg://"
                "alphainvest:secure-password@"
                "db.example.com:5432/alphainvest"
            ),
            database_ssl_mode="disable",
            jwt_secret_key=(
                "a-very-long-production-secret-key-"
                "for-alphainvest"
            ),
        )


@pytest.mark.unit
def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(
        ValidationError,
        match="APP_CORS_ORIGINS",
    ):
        Settings(
            _env_file=None,
            env="production",
            debug=False,
            database_url=(
                "postgresql+asyncpg://"
                "alphainvest:secure-password@"
                "db.example.com:5432/alphainvest"
            ),
            database_ssl_mode="require",
            jwt_secret_key=(
                "a-very-long-production-secret-key-"
                "for-alphainvest"
            ),
            cors_origins=[
                "*",
            ],
        )


@pytest.mark.unit
def test_rejects_unsupported_jwt_algorithm() -> None:
    with pytest.raises(
        ValidationError,
        match="jwt_algorithm",
    ):
        Settings(
            _env_file=None,
            jwt_algorithm="none",
        )