from alphainvest.core.config import Settings
from alphainvest.modules.market.domain.provider import (
    MarketDataProvider,
)
from alphainvest.modules.market.infrastructure.providers.alpha_vantage import (
    AlphaVantageProvider,
)
from alphainvest.modules.market.infrastructure.providers.yahoo_finance import (
    YahooFinanceProvider,
)


def create_alpha_vantage_provider(
    settings: Settings,
) -> MarketDataProvider:
    return AlphaVantageProvider(
        api_key=settings.alpha_vantage_api_key,
        base_url=settings.alpha_vantage_base_url,
        timeout_seconds=(
            settings.alpha_vantage_timeout_seconds
        ),
        output_size=settings.alpha_vantage_output_size,
    )

def create_yahoo_finance_provider() -> MarketDataProvider:
    return YahooFinanceProvider()