from datetime import date
from decimal import Decimal

import pytest

from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)

pytestmark = pytest.mark.unit


def test_daily_price_normalizes_currency() -> None:
    price = DailyPricePoint(
        date=date(2026, 7, 31),
        open=Decimal("210"),
        high=Decimal("215"),
        low=Decimal("208"),
        close=Decimal("214"),
        adjusted_close=None,
        volume=Decimal("1000"),
        currency="usd",
    )

    assert price.currency == "USD"


def test_daily_price_rejects_invalid_range() -> None:
    with pytest.raises(
        ValueError,
        match="máximo no puede ser menor",
    ):
        DailyPricePoint(
            date=date(2026, 7, 31),
            open=Decimal("210"),
            high=Decimal("205"),
            low=Decimal("208"),
            close=Decimal("204"),
            adjusted_close=None,
            volume=Decimal("1000"),
            currency="USD",
        )


def test_daily_price_rejects_negative_values() -> None:
    with pytest.raises(
        ValueError,
        match="no pueden ser negativos",
    ):
        DailyPricePoint(
            date=date(2026, 7, 31),
            open=Decimal("-1"),
            high=Decimal("215"),
            low=Decimal("208"),
            close=Decimal("214"),
            adjusted_close=None,
            volume=Decimal("1000"),
            currency="USD",
        )