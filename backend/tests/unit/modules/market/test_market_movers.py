from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.market.application.service import (
    MarketService,
)

pytestmark = pytest.mark.unit


def build_row(symbol: str, previous: str, last: str) -> dict[str, object]:
    return {
        "asset_id": uuid4(),
        "symbol": symbol,
        "name": f"{symbol} Inc.",
        "currency": "USD",
        "source_name": "Yahoo Finance",
        "last_date": date(2026, 9, 23),
        "last_close": Decimal(last),
        "previous_date": date(2026, 9, 22),
        "previous_close": Decimal(previous),
    }


@pytest.mark.asyncio
async def test_market_movers_ranks_by_percentage() -> None:
    repository = SimpleNamespace(
        list_latest_price_changes=AsyncMock(
            return_value=[
                build_row("META", "736.60", "744.10"),  # +1.02 %
                build_row("AMZN", "254.98", "249.27"),  # -2.24 %
                build_row("AAPL", "339.75", "337.02"),  # -0.80 %
                build_row("NVDA", "200.00", "210.00"),  # +5.00 %
                build_row("SPY", "100.00", "100.00"),  # 0 %
            ]
        )
    )

    movers = await MarketService(repository).get_market_movers(
        limit=5,
        preferred_source_name="Yahoo Finance",
    )

    assert [item.symbol for item in movers.gainers] == ["NVDA", "META"]
    assert [item.symbol for item in movers.losers] == ["AMZN", "AAPL"]
    assert movers.gainers[0].change == Decimal("10.00")
    assert movers.gainers[0].change_percentage == Decimal("5.0000")
    assert movers.losers[0].change_percentage == Decimal("-2.2394")
    repository.list_latest_price_changes.assert_awaited_once_with(
        preferred_source_name="Yahoo Finance",
    )


@pytest.mark.asyncio
async def test_market_movers_respects_limit() -> None:
    rows = [
        build_row(f"S{index}", "100", str(100 + index))
        for index in range(1, 8)
    ]
    repository = SimpleNamespace(
        list_latest_price_changes=AsyncMock(return_value=rows)
    )

    movers = await MarketService(repository).get_market_movers(
        limit=3,
        preferred_source_name="Yahoo Finance",
    )

    assert [item.symbol for item in movers.gainers] == ["S7", "S6", "S5"]
    assert movers.losers == []
