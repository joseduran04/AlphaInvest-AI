from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pandas as pd
import pytest

from alphainvest.modules.market.domain.exceptions import (
    ProviderResponseError,
)
from alphainvest.modules.market.infrastructure.providers.yahoo_finance import (
    YahooFinanceProvider,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_provider_normalizes_history() -> None:
    index = pd.DatetimeIndex(
        [
            datetime(2026, 7, 30),
            datetime(2026, 7, 31),
        ]
    )

    history = pd.DataFrame(
        {
            "Open": [205.0, 210.0],
            "High": [211.0, 215.0],
            "Low": [204.0, 208.0],
            "Close": [210.0, 214.5],
            "Adj Close": [209.5, 214.0],
            "Volume": [900000, 1000000],
        },
        index=index,
    )

    provider = YahooFinanceProvider()

    with patch.object(
        provider,
        "_download_history",
        return_value=history,
    ):
        prices = await provider.fetch_daily_prices(
            symbol="aapl",
            currency="usd",
            asset_type="ACCION",
        )

    assert len(prices) == 2

    assert (
        prices[0].date.isoformat()
        == "2026-07-30"
    )

    assert prices[1].close == Decimal("214.5")

    assert (
        prices[1].adjusted_close
        == Decimal("214.0")
    )

    assert prices[1].currency == "USD"


@pytest.mark.asyncio
async def test_provider_rejects_empty_history() -> None:
    provider = YahooFinanceProvider()

    with patch.object(
        provider,
        "_download_history",
        return_value=pd.DataFrame(),
    ):
        with pytest.raises(
            ProviderResponseError
        ):
            await provider.fetch_daily_prices(
                symbol="AAPL",
                currency="USD",
                asset_type="ACCION",
            )


def test_provider_source_name() -> None:
    provider = YahooFinanceProvider()

    assert provider.source_name == "Yahoo Finance"

def build_history(rows: dict[str, list[object]]) -> pd.DataFrame:
    index = pd.DatetimeIndex(
        [datetime(2026, 9, 22 + offset) for offset in range(len(rows["Open"]))]
    )
    return pd.DataFrame(rows, index=index)


@pytest.mark.asyncio
async def test_provider_widens_inconsistent_high_low() -> None:
    """Yahoo con repair=True puede dar un cierre fuera de máximo/mínimo."""

    history = build_history(
        {
            "Open": [744.35],
            "High": [770.0],
            "Low": [743.006],
            "Close": [770.815],
            "Adj Close": [770.815],
            "Volume": [23861392],
        }
    )
    provider = YahooFinanceProvider()

    with patch.object(provider, "_download_history", return_value=history):
        prices = await provider.fetch_daily_prices(
            symbol="META",
            currency="USD",
            asset_type="ACCION",
        )

    assert prices[0].high == Decimal("770.815")
    assert prices[0].low == Decimal("743.006")


@pytest.mark.asyncio
async def test_provider_accepts_missing_volume_and_skips_bad_rows() -> None:
    history = build_history(
        {
            "Open": [1.17, float("nan")],
            "High": [1.18, 1.18],
            "Low": [1.16, 1.16],
            "Close": [1.175, 1.17],
            "Adj Close": [1.175, 1.17],
            "Volume": [float("nan"), 0],
        }
    )
    provider = YahooFinanceProvider()

    with patch.object(provider, "_download_history", return_value=history):
        prices = await provider.fetch_daily_prices(
            symbol="EUR/USD",
            currency="USD",
            asset_type="DIVISA",
            market_code="FOREX",
        )

    assert len(prices) == 1
    assert prices[0].volume is None


@pytest.mark.asyncio
async def test_provider_fails_when_every_row_is_invalid() -> None:
    history = build_history(
        {
            "Open": [float("nan")],
            "High": [1.0],
            "Low": [1.0],
            "Close": [1.0],
            "Adj Close": [1.0],
            "Volume": [0],
        }
    )
    provider = YahooFinanceProvider()

    with (
        patch.object(provider, "_download_history", return_value=history),
        pytest.raises(ProviderResponseError),
    ):
        await provider.fetch_daily_prices(
            symbol="AAPL",
            currency="USD",
            asset_type="ACCION",
        )
