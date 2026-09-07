from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedAsset,
    HistoricalAlignedSimulation,
    HistoricalPortfolioEvolution,
    HistoricalPortfolioPoint,
    HistoricalPositionValue,
    HistoricalPricePoint,
)
from alphainvest.modules.simulation.domain.historical_metrics import (
    HistoricalMetricsCalculator,
)

pytestmark = pytest.mark.unit


def build_simulation(
    *,
    dates: tuple[date, ...],
    risk_free_rate: Decimal | None = None,
) -> HistoricalAlignedSimulation:
    asset_id = uuid4()

    return HistoricalAlignedSimulation(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=dates[0],
        requested_end_date=dates[-1],
        effective_start_date=dates[0],
        effective_end_date=dates[-1],
        common_dates=dates,
        assets=(
            HistoricalAlignedAsset(
                asset_id=asset_id,
                assigned_percentage=Decimal("100"),
                prices=tuple(
                    HistoricalPricePoint(
                        date=point_date,
                        price=Decimal("100"),
                    )
                    for point_date in dates
                ),
            ),
        ),
        risk_free_rate=risk_free_rate,
    )


def build_evolution(
    *,
    simulation: HistoricalAlignedSimulation,
    values: tuple[Decimal, ...],
    contributions: tuple[Decimal, ...] | None = None,
) -> HistoricalPortfolioEvolution:
    asset_id = simulation.assets[0].asset_id

    if contributions is None:
        contributions = tuple(
            Decimal("0")
            for _ in values
        )

    points = tuple(
        HistoricalPortfolioPoint(
            date=point_date,
            total_value=value,
            positions=(
                HistoricalPositionValue(
                    asset_id=asset_id,
                    price=value,
                    quantity=Decimal("1"),
                    value=value,
                ),
            ),
            contribution_amount=contribution,
        )
        for point_date, value, contribution
        in zip(
            simulation.common_dates,
            values,
            contributions,
            strict=True,
        )
    )

    return HistoricalPortfolioEvolution(
        initial_capital=simulation.initial_capital,
        currency=simulation.currency,
        points=points,
    )


def test_metrics_adjust_return_for_contribution(
) -> None:
    dates = (
        date(2024, 1, 1),
        date(2024, 1, 2),
    )

    simulation = build_simulation(
        dates=dates
    )

    evolution = build_evolution(
        simulation=simulation,
        values=(
            Decimal("1000"),
            Decimal("1100"),
        ),
        contributions=(
            Decimal("0"),
            Decimal("100"),
        ),
    )

    result = HistoricalMetricsCalculator.calculate(
        simulation=simulation,
        evolution=evolution,
    )

    assert result.daily_returns == (
        Decimal("0"),
    )

    assert (
        result.total_return_percentage
        == Decimal("0")
    )


def test_metrics_compound_total_return(
) -> None:
    dates = (
        date(2024, 1, 1),
        date(2024, 1, 2),
        date(2024, 1, 3),
    )

    simulation = build_simulation(
        dates=dates
    )

    evolution = build_evolution(
        simulation=simulation,
        values=(
            Decimal("1000"),
            Decimal("1100"),
            Decimal("1210"),
        ),
    )

    result = HistoricalMetricsCalculator.calculate(
        simulation=simulation,
        evolution=evolution,
    )

    assert result.daily_returns == (
        Decimal("0.1"),
        Decimal("0.1"),
    )

    assert (
        result.total_return_percentage
        == Decimal("21.00")
    )


def test_metrics_initial_commission_affects_total_return(
) -> None:
    dates = (
        date(2024, 1, 1),
        date(2024, 1, 2),
    )

    simulation = build_simulation(
        dates=dates
    )

    evolution = build_evolution(
        simulation=simulation,
        values=(
            Decimal("990"),
            Decimal("990"),
        ),
    )

    result = HistoricalMetricsCalculator.calculate(
        simulation=simulation,
        evolution=evolution,
    )

    assert result.daily_returns == (
        Decimal("0"),
    )

    assert (
        result.total_return_percentage
        == Decimal("-1.00")
    )


def test_metrics_calculate_sample_volatility(
) -> None:
    volatility = (
        HistoricalMetricsCalculator
        ._calculate_annualized_volatility(
            (
                Decimal("-0.1"),
                Decimal("0.1"),
            )
        )
    )

    assert volatility is not None
    assert volatility > 0


def test_metrics_zero_volatility_has_no_sharpe(
) -> None:
    dates = (
        date(2024, 1, 1),
        date(2024, 1, 2),
        date(2024, 1, 3),
    )

    simulation = build_simulation(
        dates=dates,
        risk_free_rate=Decimal("4"),
    )

    evolution = build_evolution(
        simulation=simulation,
        values=(
            Decimal("1000"),
            Decimal("1100"),
            Decimal("1210"),
        ),
    )

    result = HistoricalMetricsCalculator.calculate(
        simulation=simulation,
        evolution=evolution,
    )

    assert (
        result.annualized_volatility_percentage
        == Decimal("0")
    )

    assert result.sharpe_ratio is None


def test_metrics_calculate_maximum_drawdown(
) -> None:
    drawdown = (
        HistoricalMetricsCalculator
        ._calculate_maximum_drawdown(
            (
                Decimal("1"),
                Decimal("1.2"),
                Decimal("0.75"),
            )
        )
    )

    assert (
        drawdown
        == Decimal("0.25")
    )


def test_metrics_calculate_historical_var(
) -> None:
    value_at_risk = (
        HistoricalMetricsCalculator
        ._calculate_value_at_risk(
            daily_returns=(
                Decimal("-0.10"),
                Decimal("0"),
                Decimal("0.10"),
            ),
            final_value=Decimal("1000"),
            confidence=Decimal("0.95"),
        )
    )

    assert value_at_risk == Decimal("90.0000")


def test_metrics_require_two_returns_for_statistics(
) -> None:
    dates = (
        date(2024, 1, 1),
        date(2024, 1, 2),
    )

    simulation = build_simulation(
        dates=dates
    )

    evolution = build_evolution(
        simulation=simulation,
        values=(
            Decimal("1000"),
            Decimal("1100"),
        ),
    )

    result = HistoricalMetricsCalculator.calculate(
        simulation=simulation,
        evolution=evolution,
    )

    assert result.annualized_volatility_percentage is None
    assert result.sharpe_ratio is None
    assert result.value_at_risk is None
    assert result.value_at_risk_confidence is None


def test_metrics_reject_calendar_mismatch(
) -> None:
    simulation_dates = (
        date(2024, 1, 1),
        date(2024, 1, 2),
    )

    simulation = build_simulation(
        dates=simulation_dates
    )

    asset_id = simulation.assets[0].asset_id

    evolution = HistoricalPortfolioEvolution(
        initial_capital=Decimal("1000"),
        currency="USD",
        points=(
            HistoricalPortfolioPoint(
                date=date(2024, 1, 1),
                total_value=Decimal("1000"),
                positions=(
                    HistoricalPositionValue(
                        asset_id=asset_id,
                        price=Decimal("1000"),
                        quantity=Decimal("1"),
                        value=Decimal("1000"),
                    ),
                ),
            ),
        ),
    )

    with pytest.raises(
        ValueError,
        match="calendario",
    ):
        HistoricalMetricsCalculator.calculate(
            simulation=simulation,
            evolution=evolution,
        )