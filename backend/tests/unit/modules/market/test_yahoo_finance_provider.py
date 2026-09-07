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
            )


def test_provider_source_name() -> None:
    provider = YahooFinanceProvider()

    assert provider.source_name == "Yahoo Finance"