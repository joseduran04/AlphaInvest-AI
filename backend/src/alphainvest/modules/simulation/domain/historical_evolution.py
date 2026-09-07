from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedAsset,
    HistoricalAlignedSimulation,
    HistoricalContributionEvent,
    HistoricalContributionPlan,
    HistoricalInitialPortfolio,
    HistoricalInitialPosition,
    HistoricalPortfolioEvolution,
    HistoricalPortfolioPoint,
    HistoricalPositionValue,
)


class HistoricalPortfolioEvolutionCalculator:
    """Valoriza diariamente las posiciones virtuales."""

    @staticmethod
    def calculate(
        *,
        simulation: HistoricalAlignedSimulation,
        initial_portfolio: HistoricalInitialPortfolio,
        contribution_plan: HistoricalContributionPlan | None = None,
    ) -> HistoricalPortfolioEvolution:
        position_lookup: dict[
            UUID,
            HistoricalInitialPosition,
        ] = {
            position.asset_id: position
            for position in initial_portfolio.positions
        }

        if len(position_lookup) != len(
            initial_portfolio.positions
        ):
            raise ValueError(
                "El portafolio inicial contiene "
                "activos duplicados"
            )

        simulation_asset_ids = {
            asset.asset_id
            for asset in simulation.assets
        }

        if simulation_asset_ids != set(
            position_lookup
        ):
            raise ValueError(
                "Las posiciones iniciales no coinciden "
                "con los activos de la simulación"
            )

        quantities = {
            asset_id: position.initial_quantity
            for asset_id, position
            in position_lookup.items()
        }

        events_by_date = (
            HistoricalPortfolioEvolutionCalculator
            ._group_contributions_by_date(
                contribution_plan
            )
        )

        points: list[HistoricalPortfolioPoint] = []

        for date_index, current_date in enumerate(
            simulation.common_dates
        ):
            events = events_by_date.get(
                current_date,
                (),
            )

            contribution_amount = Decimal("0")
            commission_amount = Decimal("0")

            for event in events:
                contribution_amount += (
                    event.gross_amount
                )
                commission_amount += (
                    event.commission_amount
                )

                for purchase in event.purchases:
                    quantities[purchase.asset_id] += (
                        purchase.quantity_acquired
                    )

            points.append(
                HistoricalPortfolioEvolutionCalculator
                ._build_portfolio_point(
                    simulation=simulation,
                    quantities=quantities,
                    date_index=date_index,
                    contribution_amount=(
                        contribution_amount
                    ),
                    commission_amount=commission_amount,
                )
            )

        return HistoricalPortfolioEvolution(
            initial_capital=simulation.initial_capital,
            currency=simulation.currency,
            points=tuple(points),
        )

    @staticmethod
    def _group_contributions_by_date(
        contribution_plan: HistoricalContributionPlan | None,
    ) -> dict[
        date,
        tuple[HistoricalContributionEvent, ...],
    ]:
        if contribution_plan is None:
            return {}

        grouped: dict[
            date,
            list[HistoricalContributionEvent],
        ] = {}

        for event in contribution_plan.events:
            grouped.setdefault(
                event.execution_date,
                [],
            ).append(event)

        return {
            execution_date: tuple(events)
            for execution_date, events
            in grouped.items()
        }

    @staticmethod
    def _build_portfolio_point(
        *,
        simulation: HistoricalAlignedSimulation,
        quantities: dict[UUID, Decimal],
        date_index: int,
        contribution_amount: Decimal,
        commission_amount: Decimal,
    ) -> HistoricalPortfolioPoint:
        position_values = tuple(
            HistoricalPortfolioEvolutionCalculator
            ._build_position_value(
                asset=asset,
                quantity=quantities[asset.asset_id],
                date_index=date_index,
            )
            for asset in simulation.assets
        )

        total_value = sum(
            (
                position.value
                for position in position_values
            ),
            start=Decimal("0"),
        )

        return HistoricalPortfolioPoint(
            date=simulation.common_dates[date_index],
            total_value=total_value,
            positions=position_values,
            contribution_amount=contribution_amount,
            commission_amount=commission_amount,
        )

    @staticmethod
    def _build_position_value(
        *,
        asset: HistoricalAlignedAsset,
        quantity: Decimal,
        date_index: int,
    ) -> HistoricalPositionValue:
        price = asset.prices[date_index].price
        value = quantity * price

        return HistoricalPositionValue(
            asset_id=asset.asset_id,
            price=price,
            quantity=quantity,
            value=value,
        )