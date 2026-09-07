from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
)
from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedSimulation,
    HistoricalContributionEvent,
    HistoricalContributionPlan,
    HistoricalContributionPurchase,
)


class HistoricalContributionPlanner:
    """Programa y calcula las aportaciones periódicas."""

    @staticmethod
    def calculate(
        simulation: HistoricalAlignedSimulation,
    ) -> HistoricalContributionPlan:
        if simulation.periodic_contribution == 0:
            return HistoricalContributionPlan(
                events=(),
                total_contributions=Decimal("0"),
                total_commissions=Decimal("0"),
            )

        frequency = simulation.contribution_frequency

        if frequency is None:
            raise ValueError(
                "La frecuencia de aportación es obligatoria"
            )

        events: list[HistoricalContributionEvent] = []

        occurrence = 1

        while True:
            target_date = (
                HistoricalContributionPlanner
                ._calculate_target_date(
                    anchor=simulation.effective_start_date,
                    frequency=frequency,
                    occurrence=occurrence,
                )
            )

            if target_date > simulation.effective_end_date:
                break

            execution_date = (
                HistoricalContributionPlanner
                ._find_execution_date(
                    target_date=target_date,
                    common_dates=simulation.common_dates,
                )
            )

            if execution_date is None:
                break

            events.append(
                HistoricalContributionPlanner
                ._build_event(
                    simulation=simulation,
                    target_date=target_date,
                    execution_date=execution_date,
                )
            )

            occurrence += 1

        event_tuple = tuple(events)

        return HistoricalContributionPlan(
            events=event_tuple,
            total_contributions=sum(
                (
                    event.gross_amount
                    for event in event_tuple
                ),
                start=Decimal("0"),
            ),
            total_commissions=sum(
                (
                    event.commission_amount
                    for event in event_tuple
                ),
                start=Decimal("0"),
            ),
        )

    @staticmethod
    def _calculate_target_date(
        *,
        anchor: date,
        frequency: ContributionFrequency,
        occurrence: int,
    ) -> date:
        if frequency == ContributionFrequency.WEEKLY:
            return anchor + timedelta(
                days=7 * occurrence
            )

        if frequency == ContributionFrequency.BIWEEKLY:
            return anchor + timedelta(
                days=14 * occurrence
            )

        month_multiplier = {
            ContributionFrequency.MONTHLY: 1,
            ContributionFrequency.QUARTERLY: 3,
            ContributionFrequency.SEMIANNUAL: 6,
            ContributionFrequency.ANNUAL: 12,
        }

        months = (
            month_multiplier[frequency]
            * occurrence
        )

        return HistoricalContributionPlanner._add_months(
            anchor=anchor,
            months=months,
        )

    @staticmethod
    def _add_months(
        *,
        anchor: date,
        months: int,
    ) -> date:
        total_months = (
            anchor.year * 12
            + anchor.month
            - 1
            + months
        )

        year = total_months // 12
        month = total_months % 12 + 1

        day = min(
            anchor.day,
            monthrange(year, month)[1],
        )

        return date(
            year,
            month,
            day,
        )

    @staticmethod
    def _find_execution_date(
        *,
        target_date: date,
        common_dates: tuple[date, ...],
    ) -> date | None:
        return next(
            (
                common_date
                for common_date in common_dates
                if common_date >= target_date
            ),
            None,
        )

    @staticmethod
    def _build_event(
        *,
        simulation: HistoricalAlignedSimulation,
        target_date: date,
        execution_date: date,
    ) -> HistoricalContributionEvent:
        date_index = simulation.common_dates.index(
            execution_date
        )

        purchases = tuple(
            HistoricalContributionPlanner
            ._build_purchase(
                simulation=simulation,
                asset_index=asset_index,
                date_index=date_index,
            )
            for asset_index in range(
                len(simulation.assets)
            )
        )

        commission_amount = sum(
            (
                purchase.commission_amount
                for purchase in purchases
            ),
            start=Decimal("0"),
        )

        return HistoricalContributionEvent(
            target_date=target_date,
            execution_date=execution_date,
            gross_amount=simulation.periodic_contribution,
            commission_amount=commission_amount,
            purchases=purchases,
        )

    @staticmethod
    def _build_purchase(
        *,
        simulation: HistoricalAlignedSimulation,
        asset_index: int,
        date_index: int,
    ) -> HistoricalContributionPurchase:
        asset = simulation.assets[asset_index]

        gross_amount = (
            simulation.periodic_contribution
            * asset.assigned_percentage
            / Decimal("100")
        )

        commission_rate = (
            simulation.commission_percentage
            / Decimal("100")
        )

        net_invested_amount = (
            gross_amount
            / (
                Decimal("1")
                + commission_rate
            )
        )

        commission_amount = (
            gross_amount
            - net_invested_amount
        )

        price = asset.prices[date_index].price

        quantity_acquired = (
            net_invested_amount
            / price
        )

        return HistoricalContributionPurchase(
            asset_id=asset.asset_id,
            gross_amount=gross_amount,
            net_invested_amount=net_invested_amount,
            commission_amount=commission_amount,
            price=price,
            quantity_acquired=quantity_acquired,
        )