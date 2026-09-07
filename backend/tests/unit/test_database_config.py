import pytest
from pydantic import ValidationError

from alphainvest.core.config import Settings


def test_database_url_requires_asyncpg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "APP_DATABASE_URL",
        "postgresql://user:pass@localhost/db",
    )

    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
        )


def test_alembic_url_uses_psycopg(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "APP_DATABASE_URL",
        (
            "postgresql+asyncpg://"
            "user:pass@localhost:5432/db"
        ),
    )

    settings = Settings(
        _env_file=None,
    )

    assert settings.alembic_database_url.startswith(
        "postgresql+psycopg://"
    )


def test_alembic_url_disables_ssl_by_default() -> None:
    settings = Settings(
        _env_file=None,
        database_url=(
            "postgresql+asyncpg://"
            "user:pass@localhost:5432/db"
        ),
    )

    assert "sslmode=disable" in settings.alembic_database_url


def test_alembic_url_uses_required_ssl() -> None:
    settings = Settings(
        _env_file=None,
        database_url=(
            "postgresql+asyncpg://"
            "user:pass@db.example.com:5432/db"
        ),
        database_ssl_mode="require",
    )

    assert "sslmode=require" in settings.alembic_database_url


def test_alembic_url_uses_ssl_ca_file() -> None:
    settings = Settings(
        _env_file=None,
        database_url=(
            "postgresql+asyncpg://"
            "user:pass@db.example.com:5432/db"
        ),
        database_ssl_mode="verify-full",
        database_ssl_ca_file="/certs/supabase-ca.crt",
    )

    alembic_url = settings.alembic_database_url

    assert "sslmode=verify-full" in alembic_url
    assert "sslrootcert=" in alembic_url
    assert "supabase-ca.crt" in alembic_url