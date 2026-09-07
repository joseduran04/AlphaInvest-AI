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
    prices: tuple[Decimal, ...],
) -> HistoricalAssetInput:
    dates = (
        date(2024, 1, 1),
        date(2024, 1, 8),
        date(2024, 1, 15),
    )

    return HistoricalAssetInput(
        asset_id=uuid4(),
        assigned_percentage=percentage,
        prices=tuple(
            HistoricalPricePoint(
                date=point_date,
                price=price,
            )
            for point_date, price in zip(
                dates,
                prices,
                strict=True,
            )
        ),
    )


def test_engine_runs_complete_historical_flow(
) -> None:
    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 15),
        assets=(
            build_asset(
                percentage=Decimal("60"),
                prices=(
                    Decimal("100"),
                    Decimal("110"),
                    Decimal("120"),
                ),
            ),
            build_asset(
                percentage=Decimal("40"),
                prices=(
                    Decimal("200"),
                    Decimal("190"),
                    Decimal("210"),
                ),
            ),
        ),
        risk_free_rate=Decimal("4"),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert result.initial_capital == Decimal("10000")
    assert result.total_contributions == Decimal("0")

    assert (
        result.effective_start_date
        == date(2024, 1, 1)
    )

    assert (
        result.effective_end_date
        == date(2024, 1, 15)
    )

    assert len(result.evolution.points) == 3

    assert (
        result.final_capital
        == result.evolution.points[-1].total_value
    )

    assert (
        result.profit_loss
        == (
            result.final_capital
            - Decimal("10000")
        )
    )

    assert result.metrics.daily_returns


def test_engine_consolidates_periodic_contributions(
) -> None:
    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 15),
        assets=(
            build_asset(
                percentage=Decimal("100"),
                prices=(
                    Decimal("100"),
                    Decimal("100"),
                    Decimal("100"),
                ),
            ),
        ),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.WEEKLY
        ),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert (
        result.total_contributions
        == Decimal("200")
    )

    assert (
        result.final_capital
        == Decimal("1200")
    )

    assert (
        result.profit_loss
        == Decimal("0")
    )

    assert (
        result.metrics.total_return_percentage
        == Decimal("0")
    )


def test_engine_consolidates_commissions(
) -> None:
    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 15),
        assets=(
            build_asset(
                percentage=Decimal("100"),
                prices=(
                    Decimal("100"),
                    Decimal("100"),
                    Decimal("100"),
                ),
            ),
        ),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.WEEKLY
        ),
        commission_percentage=Decimal("1"),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert result.total_commissions > 0

    assert (
        result.total_commissions
        == (
            result.initial_portfolio.total_commission
            + result.contribution_plan.total_commissions
        )
    )

    assert result.final_capital < Decimal("1200")

    assert result.profit_loss < 0

    assert (
        result.metrics.total_return_percentage
        < 0
    )


def test_engine_normalizes_currency(
) -> None:
    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="usd",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 15),
        assets=(
            build_asset(
                percentage=Decimal("100"),
                prices=(
                    Decimal("100"),
                    Decimal("100"),
                    Decimal("100"),
                ),
            ),
        ),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert result.currency == "USD"


def test_engine_preserves_financial_metrics(
) -> None:
    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 15),
        assets=(
            build_asset(
                percentage=Decimal("100"),
                prices=(
                    Decimal("100"),
                    Decimal("110"),
                    Decimal("99"),
                ),
            ),
        ),
        risk_free_rate=Decimal("4"),
    )

    result = HistoricalSimulationEngine.run(
        simulation
    )

    assert (
        result.metrics.maximum_drawdown_percentage
        > 0
    )

    assert (
        result.metrics.annualized_volatility_percentage
        is not None
    )

    assert (
        result.metrics.value_at_risk_confidence
        == Decimal("0.95")
    )