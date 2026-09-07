from alphainvest.modules.simulation.domain.historical import (
    HistoricalSimulationInput,
    HistoricalSimulationResult,
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
from alphainvest.modules.simulation.domain.historical_metrics import (
    HistoricalMetricsCalculator,
)
from alphainvest.modules.simulation.domain.historical_purchase import (
    HistoricalInitialPurchaseCalculator,
)


class HistoricalSimulationEngine:
    """Orquesta el motor histórico completo."""

    @staticmethod
    def run(
        simulation: HistoricalSimulationInput,
    ) -> HistoricalSimulationResult:
        aligned_simulation = (
            HistoricalCalendarAligner.align(
                simulation
            )
        )

        initial_portfolio = (
            HistoricalInitialPurchaseCalculator
            .calculate(
                aligned_simulation
            )
        )

        contribution_plan = (
            HistoricalContributionPlanner
            .calculate(
                aligned_simulation
            )
        )

        evolution = (
            HistoricalPortfolioEvolutionCalculator
            .calculate(
                simulation=aligned_simulation,
                initial_portfolio=initial_portfolio,
                contribution_plan=contribution_plan,
            )
        )

        metrics = (
            HistoricalMetricsCalculator.calculate(
                simulation=aligned_simulation,
                evolution=evolution,
            )
        )

        final_capital = (
            evolution.points[-1].total_value
        )

        total_contributions = (
            contribution_plan.total_contributions
        )

        profit_loss = (
            final_capital
            - aligned_simulation.initial_capital
            - total_contributions
        )

        total_commissions = (
            initial_portfolio.total_commission
            + contribution_plan.total_commissions
        )

        return HistoricalSimulationResult(
            initial_capital=(
                aligned_simulation.initial_capital
            ),
            total_contributions=total_contributions,
            final_capital=final_capital,
            profit_loss=profit_loss,
            total_commissions=total_commissions,
            currency=aligned_simulation.currency,
            effective_start_date=(
                aligned_simulation.effective_start_date
            ),
            effective_end_date=(
                aligned_simulation.effective_end_date
            ),
            initial_portfolio=initial_portfolio,
            contribution_plan=contribution_plan,
            evolution=evolution,
            metrics=metrics,
        )