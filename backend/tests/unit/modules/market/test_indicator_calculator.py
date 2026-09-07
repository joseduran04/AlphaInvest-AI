from datetime import date, timedelta
from decimal import Decimal

import pytest

from alphainvest.modules.market.domain.indicator_calculator import (
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
    calculate_volatility,
)
from alphainvest.modules.market.domain.indicator_values import (
    ClosingPricePoint,
)

pytestmark = pytest.mark.unit


def build_prices(
    values: list[str],
) -> list[ClosingPricePoint]:
    start = date(2026, 1, 1)

    return [
        ClosingPricePoint(
            date=start + timedelta(days=index),
            close=Decimal(value),
        )
        for index, value in enumerate(values)
    ]


def test_calculates_sma() -> None:
    prices = build_prices(
        ["10", "11", "12", "13", "14"]
    )

    result = calculate_sma(
        prices,
        period=3,
    )

    assert len(result) == 3
    assert result[0].value == Decimal("11")
    assert result[-1].value == Decimal("13")
    assert result[-1].period == "3D"


def test_calculates_ema() -> None:
    prices = build_prices(
        ["10", "11", "12", "13", "14"]
    )

    result = calculate_ema(
        prices,
        period=3,
    )

    assert len(result) == 3
    assert result[0].value == Decimal("11")
    assert result[1].value == Decimal("12")
    assert result[2].value == Decimal("13")


def test_rsi_is_one_hundred_when_no_losses() -> None:
    prices = build_prices(
        ["10", "11", "12", "13", "14"]
    )

    result = calculate_rsi(
        prices,
        period=3,
    )

    assert result[0].value == Decimal("100")
    assert result[-1].value == Decimal("100")


def test_volatility_is_zero_for_constant_returns() -> None:
    prices = build_prices(
        ["10", "11", "12.1", "13.31", "14.641"]
    )

    result = calculate_volatility(
        prices,
        period=3,
    )

    assert len(result) == 2
    assert abs(result[-1].value) < Decimal(
        "0.00000001"
    )


@pytest.mark.parametrize(
    "calculator",
    [
        calculate_sma,
        calculate_ema,
    ],
)
def test_rejects_insufficient_prices(
    calculator,
) -> None:
    prices = build_prices(["10", "11"])

    with pytest.raises(
        ValueError,
        match="precios suficientes",
    ):
        calculator(
            prices,
            period=3,
        )

def test_calculates_macd_three_series() -> None:
    prices = build_prices(
        [
            str(100 + index)
            for index in range(40)
        ]
    )

    result = calculate_macd(
        prices,
        fast_period=3,
        slow_period=5,
        signal_period=3,
    )

    macd = [
        point
        for point in result
        if point.indicator_type == "MACD"
    ]
    signal = [
        point
        for point in result
        if point.indicator_type == "MACD_SIGNAL"
    ]
    histogram = [
        point
        for point in result
        if point.indicator_type
        == "MACD_HISTOGRAMA"
    ]

    assert len(macd) == 36
    assert len(signal) == 34
    assert len(histogram) == 34

    assert all(
        point.period == "3-5-3"
        for point in result
    )

    assert signal[0].date == histogram[0].date
    assert (
        histogram[0].value
        == macd[2].value - signal[0].value
    )


def test_macd_rejects_invalid_period_order() -> None:
    prices = build_prices(
        [
            str(100 + index)
            for index in range(20)
        ]
    )

    with pytest.raises(
        ValueError,
        match="periodo lento",
    ):
        calculate_macd(
            prices,
            fast_period=5,
            slow_period=3,
            signal_period=2,
        )


def test_macd_rejects_insufficient_prices() -> None:
    prices = build_prices(
        [
            str(100 + index)
            for index in range(10)
        ]
    )

    with pytest.raises(
        ValueError,
        match="precios suficientes",
    ):
        calculate_macd(
            prices,
            fast_period=3,
            slow_period=8,
            signal_period=5,
        )