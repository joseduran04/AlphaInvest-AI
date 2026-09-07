import pytest

import alphainvest.main as main_module
from alphainvest.core.config import Settings


@pytest.mark.unit
def test_local_environment_exposes_api_documentation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        _env_file=None,
        env="local",
    )

    monkeypatch.setattr(
        main_module,
        "get_settings",
        lambda: settings,
    )

    app = main_module.create_app()

    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert app.openapi_url == "/openapi.json"


@pytest.mark.unit
def test_production_environment_disables_api_documentation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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

    monkeypatch.setattr(
        main_module,
        "get_settings",
        lambda: settings,
    )

    app = main_module.create_app()

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None