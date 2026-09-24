import pytest

from alphainvest.core.config import Settings
from alphainvest.modules.market.infrastructure.providers.alpha_vantage import (
    AlphaVantageProvider,
)
from alphainvest.modules.market.infrastructure.providers.factory import (
    create_market_data_provider,
    create_market_data_providers,
)
from alphainvest.modules.market.infrastructure.providers.yahoo_finance import (
    YahooFinanceProvider,
)

pytestmark = pytest.mark.unit


def build_settings(**overrides: str) -> Settings:
    return Settings(
        _env_file=None,
        database_url="postgresql+asyncpg://user:password@localhost/test",
        **overrides,  # type: ignore[arg-type]
    )


def test_default_providers_are_yahoo_then_alpha_vantage() -> None:
    providers = create_market_data_providers(build_settings())

    assert isinstance(providers[0], YahooFinanceProvider)
    assert isinstance(providers[1], AlphaVantageProvider)


def test_providers_follow_configured_priority() -> None:
    providers = create_market_data_providers(
        build_settings(market_price_sources="Alpha Vantage")
    )

    assert len(providers) == 1
    assert isinstance(providers[0], AlphaVantageProvider)


def test_unknown_provider_name_is_rejected() -> None:
    with pytest.raises(ValueError):
        create_market_data_provider(build_settings(), "Bloomberg")
