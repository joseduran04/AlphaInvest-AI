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
    HistoricalPricePoint,
)
from alphainvest.modules.simulation.domain.historical_contributions import (
    HistoricalContributionPlanner,
)

pytestmark = pytest.mark.unit


def build_simulation(
    *,
    start_date: date = date(2024, 1, 31),
    contribution: Decimal = Decimal("1000"),
    commission: Decimal = Decimal("0"),
) -> HistoricalAlignedSimulation:
    dates = (
        date(2024, 1, 31),
        date(2024, 2, 29),
        date(2024, 4, 1),
        date(2024, 4, 30),
    )

    asset_id = uuid4()

    return HistoricalAlignedSimulation(
        initial_capital=Decimal("10000"),
        currency="USD",
        requested_start_date=start_date,
        requested_end_date=date(2024, 5, 1),
        effective_start_date=start_date,
        effective_end_date=date(2024, 4, 30),
        common_dates=dates,
        assets=(
            HistoricalAlignedAsset(
                asset_id=asset_id,
                assigned_percentage=Decimal("100"),
                prices=tuple(
                    HistoricalPricePoint(
                        date=price_date,
                        price=Decimal("100"),
                    )
                    for price_date in dates
                ),
            ),
        ),
        periodic_contribution=contribution,
        contribution_frequency=(
            ContributionFrequency.MONTHLY
            if contribution > 0
            else None
        ),
        commission_percentage=commission,
    )


def test_monthly_contribution_preserves_anchor_day(
) -> None:
    plan = HistoricalContributionPlanner.calculate(
        build_simulation()
    )

    assert plan.events[0].target_date == date(
        2024,
        2,
        29,
    )

    assert plan.events[1].target_date == date(
        2024,
        3,
        31,
    )


def test_missing_market_day_uses_next_common_date(
) -> None:
    plan = HistoricalContributionPlanner.calculate(
        build_simulation()
    )

    assert (
        plan.events[1].execution_date
        == date(2024, 4, 1)
    )


def test_contribution_uses_full_budget(
) -> None:
    plan = HistoricalContributionPlanner.calculate(
        build_simulation()
    )

    assert (
        plan.events[0].gross_amount
        == Decimal("1000")
    )

    assert (
        plan.total_contributions
        == Decimal("3000")
    )


def test_commission_is_included_in_budget(
) -> None:
    plan = HistoricalContributionPlanner.calculate(
        build_simulation(
            commission=Decimal("0.10")
        )
    )

    purchase = plan.events[0].purchases[0]

    assert (
        purchase.net_invested_amount
        + purchase.commission_amount
        == Decimal("1000")
    )

    assert purchase.commission_amount > 0


def test_zero_contribution_creates_empty_plan(
) -> None:
    simulation = build_simulation(
        contribution=Decimal("0")
    )

    plan = HistoricalContributionPlanner.calculate(
        simulation
    )

    assert plan.events == ()
    assert plan.total_contributions == Decimal("0")
    assert plan.total_commissions == Decimal("0")