from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAssetInput,
    HistoricalPricePoint,
    HistoricalSimulationInput,
)
from alphainvest.modules.simulation.domain.historical_calendar import (
    HistoricalCalendarAligner,
)

pytestmark = pytest.mark.unit


def build_asset(
    *,
    percentage: Decimal,
    dates: tuple[date, ...],
) -> HistoricalAssetInput:
    return HistoricalAssetInput(
        asset_id=uuid4(),
        assigned_percentage=percentage,
        prices=tuple(
            HistoricalPricePoint(
                date=price_date,
                price=Decimal("100"),
            )
            for price_date in dates
        ),
    )


def test_align_uses_common_calendar(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("60"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
            date(2024, 1, 5),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("40"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 5),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 6),
        assets=(
            first_asset,
            second_asset,
        ),
        risk_free_rate=Decimal("4.25"),
    )

    aligned = HistoricalCalendarAligner.align(
        simulation
    )
    assert (
        aligned.risk_free_rate
        == Decimal("4.25")
    )
    assert (
        aligned.initial_capital
        == Decimal("10000")
    )
    assert aligned.currency == "USD"
    
    assert aligned.common_dates == (
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 5),
    )

    assert (
        aligned.effective_start_date
        == date(2024, 1, 2)
    )

    assert (
        aligned.effective_end_date
        == date(2024, 1, 5)
    )


def test_align_uses_latest_asset_start(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 3),
            date(2024, 1, 4),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 5),
        assets=(
            first_asset,
            second_asset,
        ),
    )

    aligned = HistoricalCalendarAligner.align(
        simulation
    )

    assert (
        aligned.effective_start_date
        == date(2024, 1, 3)
    )


def test_align_uses_earliest_asset_end(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
            date(2024, 1, 5),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 6),
        assets=(
            first_asset,
            second_asset,
        ),
    )

    aligned = HistoricalCalendarAligner.align(
        simulation
    )

    assert (
        aligned.effective_end_date
        == date(2024, 1, 4)
    )


def test_align_filters_asset_prices_to_common_dates(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 4),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 5),
        assets=(
            first_asset,
            second_asset,
        ),
    )

    aligned = HistoricalCalendarAligner.align(
        simulation
    )

    for asset in aligned.assets:
        assert tuple(
            point.date
            for point in asset.prices
        ) == (
            date(2024, 1, 2),
            date(2024, 1, 4),
        )


def test_align_rejects_non_overlapping_periods(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 2, 1),
            date(2024, 2, 2),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 3, 1),
        assets=(
            first_asset,
            second_asset,
        ),
    )

    with pytest.raises(
        ValueError,
        match="periodo histórico común",
    ):
        HistoricalCalendarAligner.align(
            simulation
        )


def test_align_rejects_period_without_common_dates(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 2),
            date(2024, 1, 4),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("50"),
        dates=(
            date(2024, 1, 3),
            date(2024, 1, 5),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 6),
        assets=(
            first_asset,
            second_asset,
        ),
    )

    with pytest.raises(
        ValueError,
        match="no comparten fechas",
    ):
        HistoricalCalendarAligner.align(
            simulation
        )