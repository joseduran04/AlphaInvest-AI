import pytest

from alphainvest.core.config import Settings


@pytest.mark.unit
def test_default_settings() -> None:
    settings = Settings(_env_file=None)

    assert settings.name == "AlphaInvest AI API"
    assert settings.version == "0.3.0"
    assert settings.env == "local"
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.log_level == "INFO"

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
    assert settings.alpha_vantage_timeout_seconds == 15.0
    assert settings.alpha_vantage_output_size == "compact"
    assert settings.worker_enabled is False
    assert settings.worker_run_on_startup is False
    assert settings.worker_run_once is False
    assert (
        settings.worker_timezone
        == "America/Mexico_City"
    )
    assert settings.worker_price_symbols == ["AAPL"]
    assert settings.worker_max_instances == 1
    assert (
        settings.worker_misfire_grace_seconds
        == 300
    )