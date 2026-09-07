from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
)
from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedAsset,
    HistoricalAlignedSimulation,
    HistoricalInitialPortfolio,
    HistoricalInitialPosition,
    HistoricalPricePoint,
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


def build_asset(
    *,
    asset_id,
    percentage: Decimal,
    prices: tuple[Decimal, ...],
) -> HistoricalAlignedAsset:
    dates = (
        date(2024, 1, 2),
        date(2024, 1, 3),
        date(2024, 1, 4),
    )

    return HistoricalAlignedAsset(
        asset_id=asset_id,
        assigned_percentage=percentage,
        prices=tuple(
            HistoricalPricePoint(
                date=price_date,
                price=price,
            )
            for price_date, price in zip(
                dates,
                prices,
                strict=True,
            )
        ),
    )


def build_scenario() -> tuple[
    HistoricalAlignedSimulation,
    HistoricalInitialPortfolio,
]:
    first_asset_id = uuid4()
    second_asset_id = uuid4()

    simulation = HistoricalAlignedSimulation(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 5),
        effective_start_date=date(2024, 1, 2),
        effective_end_date=date(2024, 1, 4),
        common_dates=(
            date(2024, 1, 2),
            date(2024, 1, 3),
            date(2024, 1, 4),
        ),
        assets=(
            build_asset(
                asset_id=first_asset_id,
                percentage=Decimal("60"),
                prices=(
                    Decimal("150"),
                    Decimal("155"),
                    Decimal("160"),
                ),
            ),
            build_asset(
                asset_id=second_asset_id,
                percentage=Decimal("40"),
                prices=(
                    Decimal("200"),
                    Decimal("190"),
                    Decimal("210"),
                ),
            ),
        ),
    )

    initial_portfolio = HistoricalInitialPortfolio(
        initial_capital=Decimal("10000"),
        currency="USD",
        effective_start_date=date(2024, 1, 2),
        positions=(
            HistoricalInitialPosition(
                asset_id=first_asset_id,
                assigned_percentage=Decimal("60"),
                allocated_capital=Decimal("6000"),
                initial_price=Decimal("150"),
                initial_quantity=Decimal("40"),
            ),
            HistoricalInitialPosition(
                asset_id=second_asset_id,
                assigned_percentage=Decimal("40"),
                allocated_capital=Decimal("4000"),
                initial_price=Decimal("200"),
                initial_quantity=Decimal("20"),
            ),
        ),
    )

    return simulation, initial_portfolio


def test_evolution_preserves_initial_value(
) -> None:
    simulation, initial_portfolio = build_scenario()

    result = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=simulation,
            initial_portfolio=initial_portfolio,
        )
    )

    assert (
        result.points[0].total_value
        == Decimal("10000")
    )


def test_evolution_calculates_daily_portfolio_value(
) -> None:
    simulation, initial_portfolio = build_scenario()

    result = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=simulation,
            initial_portfolio=initial_portfolio,
        )
    )

    assert (
        result.points[1].total_value
        == Decimal("10000")
    )

    assert (
        result.points[2].total_value
        == Decimal("10600")
    )


def test_evolution_calculates_position_values(
) -> None:
    simulation, initial_portfolio = build_scenario()

    result = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=simulation,
            initial_portfolio=initial_portfolio,
        )
    )

    last_point = result.points[-1]

    assert (
        last_point.positions[0].value
        == Decimal("6400")
    )

    assert (
        last_point.positions[1].value
        == Decimal("4200")
    )


def test_evolution_preserves_quantities(
) -> None:
    simulation, initial_portfolio = build_scenario()

    result = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=simulation,
            initial_portfolio=initial_portfolio,
        )
    )

    for point in result.points:
        assert (
            point.positions[0].quantity
            == Decimal("40")
        )
        assert (
            point.positions[1].quantity
            == Decimal("20")
        )


def test_evolution_uses_common_dates(
) -> None:
    simulation, initial_portfolio = build_scenario()

    result = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=simulation,
            initial_portfolio=initial_portfolio,
        )
    )

    assert tuple(
        point.date
        for point in result.points
    ) == simulation.common_dates


def test_evolution_rejects_position_mismatch(
) -> None:
    simulation, initial_portfolio = build_scenario()

    incomplete_portfolio = HistoricalInitialPortfolio(
        initial_capital=Decimal("6000"),
        currency="USD",
        effective_start_date=date(2024, 1, 2),
        positions=(
            initial_portfolio.positions[0],
        ),
    )

    with pytest.raises(
        ValueError,
        match="no coinciden",
    ):
        HistoricalPortfolioEvolutionCalculator.calculate(
            simulation=simulation,
            initial_portfolio=incomplete_portfolio,
        )


def test_evolution_applies_periodic_contribution(
) -> None:
    asset_id = uuid4()

    simulation = HistoricalAlignedSimulation(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 20),
        effective_start_date=date(2024, 1, 1),
        effective_end_date=date(2024, 1, 15),
        common_dates=(
            date(2024, 1, 1),
            date(2024, 1, 8),
            date(2024, 1, 15),
        ),
        assets=(
            HistoricalAlignedAsset(
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
                        price=Decimal("100"),
                    ),
                ),
            ),
        ),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.WEEKLY
        ),
        commission_percentage=Decimal("0"),
    )

    initial_portfolio = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    contribution_plan = (
        HistoricalContributionPlanner
        .calculate(simulation)
    )

    result = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=simulation,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
        )
    )

    assert (
        result.points[0].positions[0].quantity
        == Decimal("10")
    )

    assert (
        result.points[1].positions[0].quantity
        == Decimal("11")
    )

    assert (
        result.points[2].positions[0].quantity
        == Decimal("12")
    )

    assert (
        result.points[0].total_value
        == Decimal("1000")
    )

    assert (
        result.points[1].total_value
        == Decimal("1100")
    )

    assert (
        result.points[2].total_value
        == Decimal("1200")
    )

    assert (
        result.points[1].contribution_amount
        == Decimal("100")
    )

    assert (
        result.points[2].contribution_amount
        == Decimal("100")
    )


def test_evolution_applies_commission_to_contribution(
) -> None:
    asset_id = uuid4()

    simulation = HistoricalAlignedSimulation(
        initial_capital=Decimal("1000"),
        currency="USD",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 1, 10),
        effective_start_date=date(2024, 1, 1),
        effective_end_date=date(2024, 1, 8),
        common_dates=(
            date(2024, 1, 1),
            date(2024, 1, 8),
        ),
        assets=(
            HistoricalAlignedAsset(
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
                ),
            ),
        ),
        periodic_contribution=Decimal("100"),
        contribution_frequency=(
            ContributionFrequency.WEEKLY
        ),
        commission_percentage=Decimal("1"),
    )

    initial_portfolio = (
        HistoricalInitialPurchaseCalculator
        .calculate(simulation)
    )

    contribution_plan = (
        HistoricalContributionPlanner
        .calculate(simulation)
    )

    result = (
        HistoricalPortfolioEvolutionCalculator
        .calculate(
            simulation=simulation,
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
        )
    )

    event = contribution_plan.events[0]
    purchase = event.purchases[0]

    assert event.gross_amount == Decimal("100")

    assert (
        purchase.net_invested_amount
        + purchase.commission_amount
        == Decimal("100")
    )

    assert purchase.commission_amount > 0

    assert (
        result.points[1].commission_amount
        == event.commission_amount
    )

    assert (
        result.points[1].positions[0].quantity
        > result.points[0].positions[0].quantity
    )