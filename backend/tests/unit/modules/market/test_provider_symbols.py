from types import SimpleNamespace

import pytest

from alphainvest.modules.market.domain.provider_symbols import (
    news_ticker,
    yahoo_symbol,
)
from alphainvest.modules.news.application.news_tickers import (
    asset_news_ticker,
)

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("symbol", "asset_type", "market", "expected"),
    [
        ("AAPL", "ACCION", "NASDAQ", "AAPL"),
        ("WALMEX", "ACCION", "BMV", "WALMEX.MX"),
        ("GFNORTEO", "ACCION", "BMV", "GFNORTEO.MX"),
        ("FEMSAUBD", "ACCION", "BMV", "FEMSAUBD.MX"),
        # América Móvil unificó sus series: hoy cotiza como AMXB.
        ("AMXL", "ACCION", "BMV", "AMXB.MX"),
        ("USD/MXN", "DIVISA", "FOREX", "USDMXN=X"),
        ("EUR/USD", "DIVISA", "FOREX", "EURUSD=X"),
        ("BTC-USD", "CRIPTO", "CRYPTO", "BTC-USD"),
        ("SPY", "ETF", "NYSE", "SPY"),
    ],
)
def test_yahoo_symbol(
    symbol: str,
    asset_type: str,
    market: str,
    expected: str,
) -> None:
    assert (
        yahoo_symbol(
            symbol=symbol,
            asset_type=asset_type,
            market_code=market,
        )
        == expected
    )


@pytest.mark.parametrize(
    ("symbol", "asset_type", "expected"),
    [
        ("NVDA", "ACCION", "NVDA"),
        ("AMXL", "ACCION", "AMX"),
        ("FEMSAUBD", "ACCION", "FMX"),
        ("BTC-USD", "CRIPTO", "CRYPTO:BTC"),
        ("USD/MXN", "DIVISA", "FOREX:MXN"),
        ("EUR/USD", "DIVISA", "FOREX:EUR"),
    ],
)
def test_news_ticker(
    symbol: str,
    asset_type: str,
    expected: str,
) -> None:
    assert (
        news_ticker(symbol=symbol, asset_type=asset_type)
        == expected
    )


def test_asset_news_ticker_reads_asset_relations() -> None:
    asset = SimpleNamespace(
        simbolo="AMXL",
        tipo_activo=SimpleNamespace(codigo="ACCION"),
        mercado=SimpleNamespace(codigo="BMV"),
    )

    assert asset_news_ticker(asset) == "AMX"
