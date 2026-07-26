import pytest
from pydantic import ValidationError

from alphainvest.core.config import Settings


def test_database_url_requires_asyncpg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DATABASE_URL", "postgresql://user:pass@localhost/db")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_alembic_url_uses_psycopg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/db")
    settings = Settings(_env_file=None)
    assert settings.alembic_database_url.startswith("postgresql+psycopg://")
