from datetime import date

import pytest

from alphainvest.modules.market.domain.trading_calendar_exceptions import (
    InvalidTradingSessionError,
    UnsupportedMarketCalendarError,
)
from alphainvest.modules.market.infrastructure.exchange_trading_calendar import (
    ExchangeTradingCalendar,
)

pytestmark = pytest.mark.unit


def test_resolves_five_nasdaq_sessions() -> None:
    calendar = ExchangeTradingCalendar()

    result = calendar.target_session(
        market_code="NASDAQ",
        base_date=date(2026, 8, 14),
        horizon_sessions=5,
    )

    assert result == date(
        2026,
        8,
        21,
    )


def test_skips_us_market_holiday() -> None:
    calendar = ExchangeTradingCalendar()

    result = calendar.target_session(
        market_code="NASDAQ",
        base_date=date(2026, 9, 4),
        horizon_sessions=5,
    )

    assert result == date(
        2026,
        9,
        14,
    )


def test_rejects_weekend_as_base_session() -> None:
    calendar = ExchangeTradingCalendar()

    with pytest.raises(
        InvalidTradingSessionError
    ):
        calendar.target_session(
            market_code="NASDAQ",
            base_date=date(2026, 8, 15),
            horizon_sessions=5,
        )


def test_rejects_unsupported_market() -> None:
    calendar = ExchangeTradingCalendar()

    with pytest.raises(
        UnsupportedMarketCalendarError
    ):
        calendar.target_session(
            market_code="UNKNOWN",
            base_date=date(2026, 8, 14),
            horizon_sessions=5,
        )


def test_rejects_invalid_horizon() -> None:
    calendar = ExchangeTradingCalendar()

    with pytest.raises(ValueError):
        calendar.target_session(
            market_code="NASDAQ",
            base_date=date(2026, 8, 14),
            horizon_sessions=0,
        )