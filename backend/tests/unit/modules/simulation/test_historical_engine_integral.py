from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
)
from alphainvest.modules.simulation.domain.historical import (
    HistoricalAssetInput,
    HistoricalPricePoint,
    HistoricalSimulationInput,
)
from alphainvest.modules.simulation.domain.historical_engine import (
    HistoricalSimulationEngine,
)

pytestmark = pytest.mark.unit


def build_asset(
    *,
    percentage: Decimal,
    dated_prices: tuple[
        tuple[date, Decimal],
        ...,
    ],
) -> HistoricalAssetInput:
    return HistoricalAssetInput(
        asset_id=uuid4(),
        assigned_percentage=percentage,
        prices=tuple(
            HistoricalPricePoint(
                date=price_date,
                price=price,
            )
            for price_date, price in dated_prices
        ),
    )


def test_integral_aligns_different_asset_calendars(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("60"),
        dated_prices=(
            (
                date(2024, 1, 2),
                Decimal("100"),
            ),
            (
                date(2024, 1, 3),
                Decimal("105"),
            ),
            (
                date(2024, 1, 4),
                Decimal("110"),
            ),
            (
                date(2024, 1, 5),
                Decimal("115"),
            ),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("40"),
        dated_prices=(
            (
                date(2024, 1, 3),
                Decimal("200"),
            ),
            (
                date(2024, 1, 4),
                Decimal("205"),
            ),
            (
                date(2024, 1, 5),
                Decimal("210"),
            ),
            (
                date(2024, 1, 8),
                Decimal("215"),
            ),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 10),
        assets=(
            first_asset,
            second_asset,
        ),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert (
        result.effective_start_date
        == date(2024, 1, 3)
    )

    assert (
        result.effective_end_date
        == date(2024, 1, 5)
    )

    assert tuple(
        point.date
        for point in result.evolution.points
    ) == (
        date(2024, 1, 3),
        date(2024, 1, 4),
        date(2024, 1, 5),
    )


def test_integral_does_not_forward_fill_missing_date(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("50"),
        dated_prices=(
            (
                date(2024, 1, 2),
                Decimal("100"),
            ),
            (
                date(2024, 1, 3),
                Decimal("101"),
            ),
            (
                date(2024, 1, 4),
                Decimal("102"),
            ),
            (
                date(2024, 1, 5),
                Decimal("103"),
            ),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("50"),
        dated_prices=(
            (
                date(2024, 1, 2),
                Decimal("200"),
            ),
            (
                date(2024, 1, 3),
                Decimal("201"),
            ),
            (
                date(2024, 1, 5),
                Decimal("203"),
            ),
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

    result = HistoricalSimulationEngine.run(
        simulation
    )

    evolution_dates = tuple(
        point.date
        for point in result.evolution.points
    )

    assert evolution_dates == (
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 5),
    )

    assert date(2024, 1, 4) not in evolution_dates


def test_integral_moves_contribution_to_next_common_date(
) -> None:
    asset = build_asset(
        percentage=Decimal("100"),
        dated_prices=(
            (
                date(2024, 1, 1),
                Decimal("100"),
            ),
            (
                date(2024, 1, 9),
                Decimal("100"),
            ),
            (
                date(2024, 1, 15),
                Decimal("100"),
            ),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 16),
        assets=(asset,),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.WEEKLY
        ),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    first_event = (
        result.contribution_plan.events[0]
    )

    assert (
        first_event.target_date
        == date(2024, 1, 8)
    )

    assert (
        first_event.execution_date
        == date(2024, 1, 9)
    )

    point = next(
        point
        for point in result.evolution.points
        if point.date == date(2024, 1, 9)
    )

    assert (
        point.contribution_amount
        == Decimal("100")
    )

    assert (
        point.positions[0].quantity
        == Decimal("11")
    )


def test_integral_month_end_contribution_keeps_anchor(
) -> None:
    asset = build_asset(
        percentage=Decimal("100"),
        dated_prices=(
            (
                date(2024, 1, 31),
                Decimal("100"),
            ),
            (
                date(2024, 2, 29),
                Decimal("100"),
            ),
            (
                date(2024, 4, 1),
                Decimal("100"),
            ),
            (
                date(2024, 4, 30),
                Decimal("100"),
            ),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 30),
        requested_end_date=date(2024, 5, 1),
        assets=(asset,),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.MONTHLY
        ),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert tuple(
        event.target_date
        for event in result.contribution_plan.events
    ) == (
        date(2024, 2, 29),
        date(2024, 3, 31),
        date(2024, 4, 30),
    )

    assert (
        result.contribution_plan
        .events[1]
        .execution_date
        == date(2024, 4, 1)
    )


def test_integral_commissions_reduce_constant_price_result(
) -> None:
    asset = build_asset(
        percentage=Decimal("100"),
        dated_prices=(
            (
                date(2024, 1, 1),
                Decimal("100"),
            ),
            (
                date(2024, 1, 8),
                Decimal("100"),
            ),
            (
                date(2024, 1, 15),
                Decimal("100"),
            ),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 16),
        assets=(asset,),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.WEEKLY
        ),
        commission_percentage=Decimal("1"),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    contributed_capital = (
        result.initial_capital
        + result.total_contributions
    )

    assert result.total_commissions > 0

    assert (
        result.final_capital
        < contributed_capital
    )

    assert result.profit_loss < 0

    assert (
        result.metrics.total_return_percentage
        < 0
    )


def test_integral_statistics_are_none_when_insufficient(
) -> None:
    asset = build_asset(
        percentage=Decimal("100"),
        dated_prices=(
            (
                date(2024, 1, 1),
                Decimal("100"),
            ),
            (
                date(2024, 1, 2),
                Decimal("110"),
            ),
        ),
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 3),
        assets=(asset,),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert len(result.metrics.daily_returns) == 1

    assert (
        result.metrics.annualized_volatility_percentage
        is None
    )

    assert result.metrics.sharpe_ratio is None
    assert result.metrics.value_at_risk is None

    assert (
        result.metrics.value_at_risk_confidence
        is None
    )


def test_integral_rejects_non_overlapping_assets(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("50"),
        dated_prices=(
            (
                date(2024, 1, 1),
                Decimal("100"),
            ),
            (
                date(2024, 1, 2),
                Decimal("101"),
            ),
        ),
    )

    second_asset = build_asset(
        percentage=Decimal("50"),
        dated_prices=(
            (
                date(2024, 2, 1),
                Decimal("200"),
            ),
            (
                date(2024, 2, 2),
                Decimal("201"),
            ),
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
        HistoricalSimulationEngine.run(
            simulation
        )