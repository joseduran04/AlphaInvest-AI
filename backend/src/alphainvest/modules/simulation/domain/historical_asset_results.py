from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedSimulation,
    HistoricalAssetResult,
    HistoricalContributionPlan,
    HistoricalInitialPortfolio,
    HistoricalInitialPosition,
    HistoricalPortfolioEvolution,
    HistoricalPositionValue,
)

TRADING_DAYS_PER_YEAR = Decimal("252")


class HistoricalAssetResultCalculator:
    """Calcula resultados individuales de los activos."""

    @staticmethod
    def calculate(
        *,
        simulation: HistoricalAlignedSimulation,
        initial_portfolio: HistoricalInitialPortfolio,
        contribution_plan: HistoricalContributionPlan,
        evolution: HistoricalPortfolioEvolution,
    ) -> tuple[HistoricalAssetResult, ...]:
        initial_positions = {
            position.asset_id: position
            for position in initial_portfolio.positions
        }

        if len(initial_positions) != len(
            initial_portfolio.positions
        ):
            raise ValueError(
                "El portafolio inicial contiene "
                "activos duplicados"
            )

        return tuple(
            HistoricalAssetResultCalculator
            ._calculate_asset_result(
                asset_id=asset.asset_id,
                assigned_percentage=(
                    asset.assigned_percentage
                ),
                initial_position=(
                    initial_positions[asset.asset_id]
                ),
                contribution_plan=contribution_plan,
                evolution=evolution,
            )
            for asset in simulation.assets
        )

    @staticmethod
    def _calculate_asset_result(
        *,
        asset_id: UUID,
        assigned_percentage: Decimal,
        initial_position: HistoricalInitialPosition,
        contribution_plan: HistoricalContributionPlan,
        evolution: HistoricalPortfolioEvolution,
    ) -> HistoricalAssetResult:
        position_values = tuple(
            next(
                position
                for position in point.positions
                if position.asset_id == asset_id
            )
            for point in evolution.points
        )

        first_value = position_values[0]
        final_value = position_values[-1]

        contributions_by_date = (
            HistoricalAssetResultCalculator
            ._build_contributions_by_date(
                asset_id=asset_id,
                contribution_plan=contribution_plan,
            )
        )

        daily_returns = (
            HistoricalAssetResultCalculator
            ._calculate_daily_returns(
                position_values=position_values,
                evolution=evolution,
                contributions_by_date=(
                    contributions_by_date
                ),
            )
        )

        initial_factor = (
            first_value.value
            / initial_position.allocated_capital
        )

        factors = (
            initial_factor,
            *(
                Decimal("1") + daily_return
                for daily_return in daily_returns
            ),
        )

        total_return = (
            HistoricalAssetResultCalculator
            ._compound_factors(factors)
            - Decimal("1")
        )

        volatility = (
            HistoricalAssetResultCalculator
            ._calculate_volatility(
                daily_returns
            )
        )

        maximum_drawdown = (
            HistoricalAssetResultCalculator
            ._calculate_drawdown(
                factors
            )
        )

        total_contributions = sum(
            contributions_by_date.values(),
            start=Decimal("0"),
        )

        profit_loss = (
            final_value.value
            - initial_position.allocated_capital
        )

        return HistoricalAssetResult(
            asset_id=asset_id,
            assigned_percentage=assigned_percentage,
            allocated_capital=(
                initial_position.allocated_capital
            ),
            initial_quantity=(
                initial_position.initial_quantity
            ),
            initial_price=(
                initial_position.initial_price
            ),
            final_price=final_value.price,
            final_value=final_value.value,
            profit_loss=profit_loss,
            return_percentage=(
                total_return
                * Decimal("100")
            ),
            volatility_percentage=(
                volatility
                * Decimal("100")
                if volatility is not None
                else None
            ),
            maximum_drawdown_percentage=(
                maximum_drawdown
                * Decimal("100")
            ),
            total_contributions=total_contributions,
            final_quantity=final_value.quantity,
        )

    @staticmethod
    def _build_contributions_by_date(
        *,
        asset_id: UUID,
        contribution_plan: HistoricalContributionPlan,
    ) -> dict[date, Decimal]:
        contributions: dict[
            date,
            Decimal,
        ] = {}

        for event in contribution_plan.events:
            for purchase in event.purchases:
                if purchase.asset_id != asset_id:
                    continue

                previous = contributions.get(
                    event.execution_date,
                    Decimal("0"),
                )

                contributions[
                    event.execution_date
                ] = (
                    previous
                    + purchase.gross_amount
                )

        return contributions

    @staticmethod
    def _calculate_daily_returns(
        *,
        position_values: tuple[
            HistoricalPositionValue,
            ...,
        ],
        evolution: HistoricalPortfolioEvolution,
        contributions_by_date: dict[
            date,
            Decimal,
        ],
    ) -> tuple[Decimal, ...]:
        if len(position_values) < 2:
            return ()

        returns: list[Decimal] = []

        for index in range(
            1,
            len(position_values),
        ):
            previous = position_values[index - 1]
            current = position_values[index]

            current_date = (
                evolution.points[index].date
            )

            contribution = (
                contributions_by_date.get(
                    current_date,
                    Decimal("0"),
                )
            )

            adjusted_current_value = (
                current.value
                - contribution
            )

            returns.append(
                adjusted_current_value
                / previous.value
                - Decimal("1")
            )

        return tuple(returns)
    
    @staticmethod
    def _compound_factors(
        factors: tuple[Decimal, ...],
    ) -> Decimal:
        compounded = Decimal("1")

        for factor in factors:
            compounded *= factor

        return compounded

    @staticmethod
    def _calculate_volatility(
        daily_returns: tuple[Decimal, ...],
    ) -> Decimal | None:
        if len(daily_returns) < 2:
            return None

        mean = (
            sum(
                daily_returns,
                start=Decimal("0"),
            )
            / Decimal(len(daily_returns))
        )

        squared_differences = sum(
            (
                (daily_return - mean) ** 2
                for daily_return in daily_returns
            ),
            start=Decimal("0"),
        )

        variance = (
            squared_differences
            / Decimal(
                len(daily_returns) - 1
            )
        )

        return (
            variance.sqrt()
            * TRADING_DAYS_PER_YEAR.sqrt()
        )

    @staticmethod
    def _calculate_drawdown(
        factors: tuple[Decimal, ...],
    ) -> Decimal:
        index_value = Decimal("1")
        peak_value = Decimal("1")
        maximum_drawdown = Decimal("0")

        for factor in factors:
            index_value *= factor

            if index_value > peak_value:
                peak_value = index_value

            drawdown = (
                Decimal("1")
                - index_value / peak_value
            )

            if drawdown > maximum_drawdown:
                maximum_drawdown = drawdown

        return maximum_drawdown