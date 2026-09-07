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
from alphainvest.modules.simulation.domain.historical_asset_results import (
    HistoricalAssetResultCalculator,
)
from alphainvest.modules.simulation.domain.historical_calendar import (
    HistoricalCalendarAligner,
)
from alphainvest.modules.simulation.domain.historical_contributions import (
    HistoricalContributionPlanner,
)
from alphainvest.modules.simulation.domain.historical_evolution import (
    HistoricalPortfolioEvolutionCalculator,
)
from alphainvest.modules.simulation.domain.historical_purchase import (
    HistoricalInitialPurchaseCalculator,
)

pytestmark = pytest.mark.unit


def build_scenario() -> tuple:
    asset_id = uuid4()

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 15),
        assets=(
            HistoricalAssetInput(
                asset_id=asset_id,
                assigned_percentage=Decimal("100"),
                prices=(
                    HistoricalPricePoint(
                        date=date(2024, 1, 1),
                        price=Decimal("100"),
                    ),
                    HistoricalPricePoint(
                        date=date(2024, 1, 8),
                        price=Decimal("100"),
                    ),
                    HistoricalPricePoint(
                        date=date(2024, 1, 15),
                        price=Decimal("110"),
                    ),
                ),
            ),
        ),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.WEEKLY
        ),
    )

    aligned = HistoricalCalendarAligner.align(
        simulation
    )

    initial_portfolio = (
        HistoricalInitialPurchaseCalculator
        .calculate(aligned)
    )

    contribution_plan = (
        HistoricalContributionPlanner
        .calculate(aligned)
    )

    evolution = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=aligned,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
        )
    )

    return (
        aligned,
        initial_portfolio,
        contribution_plan,
        evolution,
    )


def test_asset_result_uses_initial_allocation(
) -> None:
    (
        aligned,
        initial_portfolio,
        contribution_plan,
        evolution,
    ) = build_scenario()

    result = (
        HistoricalAssetResultCalculator
        .calculate(
            simulation=aligned,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
            evolution=evolution,
        )[0]
    )

    assert (
        result.allocated_capital
        == Decimal("1000")
    )

    assert (
        result.initial_quantity
        == Decimal("10")
    )

    assert (
        result.initial_price
        == Decimal("100")
    )


def test_asset_result_uses_final_position(
) -> None:
    (
        aligned,
        initial_portfolio,
        contribution_plan,
        evolution,
    ) = build_scenario()

    result = (
        HistoricalAssetResultCalculator
        .calculate(
            simulation=aligned,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
            evolution=evolution,
        )[0]
    )

    assert (
        result.final_price
        == Decimal("110")
    )

    assert (
        result.final_value
        == evolution.points[-1].positions[0].value
    )

    assert (
        result.final_quantity
        == evolution.points[-1].positions[0].quantity
    )


def test_asset_result_tracks_contributions(
) -> None:
    (
        aligned,
        initial_portfolio,
        contribution_plan,
        evolution,
    ) = build_scenario()

    result = (
        HistoricalAssetResultCalculator
        .calculate(
            simulation=aligned,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
            evolution=evolution,
        )[0]
    )

    assert (
        result.total_contributions
        == Decimal("200")
    )


def test_asset_result_profit_loss_follows_database_semantics(
) -> None:
    (
        aligned,
        initial_portfolio,
        contribution_plan,
        evolution,
    ) = build_scenario()

    result = (
        HistoricalAssetResultCalculator
        .calculate(
            simulation=aligned,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
            evolution=evolution,
        )[0]
    )

    assert (
        result.profit_loss
        == (
            result.final_value
            - result.allocated_capital
        )
    )


def test_asset_result_calculates_adjusted_return(
) -> None:
    (
        aligned,
        initial_portfolio,
        contribution_plan,
        evolution,
    ) = build_scenario()

    result = (
        HistoricalAssetResultCalculator
        .calculate(
            simulation=aligned,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
            evolution=evolution,
        )[0]
    )

    assert result.return_percentage > 0


def test_asset_result_calculates_risk_metrics(
) -> None:
    (
        aligned,
        initial_portfolio,
        contribution_plan,
        evolution,
    ) = build_scenario()

    result = (
        HistoricalAssetResultCalculator
        .calculate(
            simulation=aligned,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
            evolution=evolution,
        )[0]
    )

    assert (
        result.volatility_percentage
        is not None
    )

    assert (
        result.volatility_percentage
        >= Decimal("0")
    )

    assert (
        result.maximum_drawdown_percentage
        is not None
    )