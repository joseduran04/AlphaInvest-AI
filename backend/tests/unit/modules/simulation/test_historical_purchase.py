from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedAsset,
    HistoricalAlignedSimulation,
    HistoricalPricePoint,
)
from alphainvest.modules.simulation.domain.historical_purchase import (
    HistoricalInitialPurchaseCalculator,
)

pytestmark = pytest.mark.unit


def build_aligned_asset(
    *,
    percentage: Decimal,
    price: Decimal,
) -> HistoricalAlignedAsset:
    return HistoricalAlignedAsset(
        asset_id=uuid4(),
        assigned_percentage=percentage,
        prices=(
            HistoricalPricePoint(
                date=date(2024, 1, 2),
                price=price,
            ),
            HistoricalPricePoint(
                date=date(2024, 1, 3),
                price=price,
            ),
        ),
    )


def build_aligned_simulation(
) -> HistoricalAlignedSimulation:
    return HistoricalAlignedSimulation(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 4),
        effective_start_date=date(2024, 1, 2),
        effective_end_date=date(2024, 1, 3),
        common_dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
        ),
        assets=(
            build_aligned_asset(
                percentage=Decimal("60"),
                price=Decimal("150"),
            ),
            build_aligned_asset(
                percentage=Decimal("40"),
                price=Decimal("200"),
            ),
        ),
    )


def test_initial_purchase_distributes_capital(
) -> None:
    simulation = build_aligned_simulation()

    result = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    assert (
        result.positions[0].allocated_capital
        == Decimal("6000")
    )

    assert (
        result.positions[1].allocated_capital
        == Decimal("4000")
    )


def test_initial_purchase_uses_effective_start_price(
) -> None:
    simulation = build_aligned_simulation()

    result = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    assert (
        result.positions[0].initial_price
        == Decimal("150")
    )

    assert (
        result.positions[1].initial_price
        == Decimal("200")
    )


def test_initial_purchase_calculates_virtual_quantity(
) -> None:
    simulation = build_aligned_simulation()

    result = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    assert (
        result.positions[0].initial_quantity
        == Decimal("40")
    )

    assert (
        result.positions[1].initial_quantity
        == Decimal("20")
    )


def test_initial_purchase_preserves_total_capital(
) -> None:
    simulation = build_aligned_simulation()

    result = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    total = sum(
        (
            position.allocated_capital
            for position in result.positions
        ),
        start=Decimal("0"),
    )

    assert total == Decimal("10000")
    assert total == result.initial_capital


def test_initial_purchase_preserves_currency_and_date(
) -> None:
    simulation = build_aligned_simulation()

    result = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    assert result.currency == "USD"
    assert (
        result.effective_start_date
        == date(2024, 1, 2)
    )


def test_initial_purchase_supports_fractional_shares(
) -> None:
    simulation = HistoricalAlignedSimulation(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 4),
        effective_start_date=date(2024, 1, 2),
        effective_end_date=date(2024, 1, 3),
        common_dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
        ),
        assets=(
            build_aligned_asset(
                percentage=Decimal("100"),
                price=Decimal("300"),
            ),
        ),
    )

    result = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    assert (
        result.positions[0].initial_quantity
        == Decimal("1000") / Decimal("300")
    )