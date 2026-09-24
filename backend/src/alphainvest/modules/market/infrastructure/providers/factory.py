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

def create_market_data_provider(
    settings: Settings,
    source_name: str,
) -> MarketDataProvider:
    """Crea el proveedor asociado a una fuente financiera por nombre."""

    if source_name == YahooFinanceProvider.source_name:
        return create_yahoo_finance_provider()

    if source_name == AlphaVantageProvider.source_name:
        return create_alpha_vantage_provider(settings)

    raise ValueError(
        f"Fuente de precios no soportada: {source_name}"
    )


def create_market_data_providers(
    settings: Settings,
) -> list[MarketDataProvider]:
    """Proveedores de precios en orden de prioridad (principal y respaldos)."""

    return [
        create_market_data_provider(settings, name)
        for name in settings.market_price_source_names
    ]
