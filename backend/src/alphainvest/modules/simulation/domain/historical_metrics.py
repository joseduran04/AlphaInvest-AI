from decimal import Decimal
from math import pow

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedSimulation,
    HistoricalMetricsResult,
    HistoricalPortfolioEvolution,
)

TRADING_DAYS_PER_YEAR = Decimal("252")
CALENDAR_DAYS_PER_YEAR = Decimal("365")
DEFAULT_VAR_CONFIDENCE = Decimal("0.95")


class HistoricalMetricsCalculator:
    """Calcula métricas financieras del backtest histórico."""

    @staticmethod
    def calculate(
        *,
        simulation: HistoricalAlignedSimulation,
        evolution: HistoricalPortfolioEvolution,
    ) -> HistoricalMetricsResult:
        if len(evolution.points) != len(
            simulation.common_dates
        ):
            raise ValueError(
                "La evolución no coincide con "
                "el calendario de la simulación"
            )

        evolution_dates = tuple(
            point.date
            for point in evolution.points
        )

        if evolution_dates != simulation.common_dates:
            raise ValueError(
                "Las fechas de evolución no coinciden "
                "con el calendario de la simulación"
            )

        daily_returns = (
            HistoricalMetricsCalculator
            ._calculate_daily_returns(evolution)
        )

        performance_factors = (
            HistoricalMetricsCalculator
            ._calculate_performance_factors(
                simulation=simulation,
                evolution=evolution,
                daily_returns=daily_returns,
            )
        )

        total_return = (
            HistoricalMetricsCalculator
            ._compound_factors(
                performance_factors
            )
            - Decimal("1")
        )

        annualized_return = (
            HistoricalMetricsCalculator
            ._calculate_annualized_return(
                total_return=total_return,
                simulation=simulation,
            )
        )

        annualized_volatility = (
            HistoricalMetricsCalculator
            ._calculate_annualized_volatility(
                daily_returns
            )
        )

        sharpe_ratio = (
            HistoricalMetricsCalculator
            ._calculate_sharpe_ratio(
                annualized_return=annualized_return,
                annualized_volatility=(
                    annualized_volatility
                ),
                risk_free_rate=(
                    simulation.risk_free_rate
                ),
            )
        )

        maximum_drawdown = (
            HistoricalMetricsCalculator
            ._calculate_maximum_drawdown(
                performance_factors
            )
        )

        value_at_risk = (
            HistoricalMetricsCalculator
            ._calculate_value_at_risk(
                daily_returns=daily_returns,
                final_value=(
                    evolution.points[-1].total_value
                ),
                confidence=DEFAULT_VAR_CONFIDENCE,
            )
        )

        return HistoricalMetricsResult(
            daily_returns=daily_returns,
            total_return_percentage=(
                total_return
                * Decimal("100")
            ),
            annualized_return_percentage=(
                annualized_return
                * Decimal("100")
                if annualized_return is not None
                else None
            ),
            annualized_volatility_percentage=(
                annualized_volatility
                * Decimal("100")
                if annualized_volatility is not None
                else None
            ),
            sharpe_ratio=sharpe_ratio,
            maximum_drawdown_percentage=(
                maximum_drawdown
                * Decimal("100")
            ),
            value_at_risk=value_at_risk,
            value_at_risk_confidence=(
                DEFAULT_VAR_CONFIDENCE
                if value_at_risk is not None
                else None
            ),
        )

    @staticmethod
    def _calculate_daily_returns(
        evolution: HistoricalPortfolioEvolution,
    ) -> tuple[Decimal, ...]:
        if len(evolution.points) < 2:
            return ()

        returns: list[Decimal] = []

        for index in range(
            1,
            len(evolution.points),
        ):
            previous = evolution.points[index - 1]
            current = evolution.points[index]

            adjusted_current_value = (
                current.total_value
                - current.contribution_amount
            )

            daily_return = (
                adjusted_current_value
                / previous.total_value
                - Decimal("1")
            )

            returns.append(daily_return)

        return tuple(returns)

    @staticmethod
    def _calculate_performance_factors(
        *,
        simulation: HistoricalAlignedSimulation,
        evolution: HistoricalPortfolioEvolution,
        daily_returns: tuple[Decimal, ...],
    ) -> tuple[Decimal, ...]:
        initial_factor = (
            evolution.points[0].total_value
            / simulation.initial_capital
        )

        return (
            initial_factor,
            *(
                Decimal("1") + daily_return
                for daily_return in daily_returns
            ),
        )

    @staticmethod
    def _compound_factors(
        factors: tuple[Decimal, ...],
    ) -> Decimal:
        compounded = Decimal("1")

        for factor in factors:
            compounded *= factor

        return compounded

    @staticmethod
    def _calculate_annualized_return(
        *,
        total_return: Decimal,
        simulation: HistoricalAlignedSimulation,
    ) -> Decimal | None:
        elapsed_days = (
            simulation.effective_end_date
            - simulation.effective_start_date
        ).days

        if elapsed_days <= 0:
            return None

        growth_factor = (
            Decimal("1")
            + total_return
        )

        if growth_factor <= 0:
            return None

        exponent = (
            CALENDAR_DAYS_PER_YEAR
            / Decimal(elapsed_days)
        )

        annualized_factor = Decimal(
            str(
                pow(
                    float(growth_factor),
                    float(exponent),
                )
            )
        )

        return (
            annualized_factor
            - Decimal("1")
        )

    @staticmethod
    def _calculate_annualized_volatility(
        daily_returns: tuple[Decimal, ...],
    ) -> Decimal | None:
        if len(daily_returns) < 2:
            return None

        count = Decimal(
            len(daily_returns)
        )

        mean = (
            sum(
                daily_returns,
                start=Decimal("0"),
            )
            / count
        )

        squared_differences = sum(
            (
                (daily_return - mean) ** 2
                for daily_return in daily_returns
            ),
            start=Decimal("0"),
        )

        sample_variance = (
            squared_differences
            / Decimal(
                len(daily_returns) - 1
            )
        )

        standard_deviation = (
            sample_variance.sqrt()
        )

        return (
            standard_deviation
            * TRADING_DAYS_PER_YEAR.sqrt()
        )

    @staticmethod
    def _calculate_sharpe_ratio(
        *,
        annualized_return: Decimal | None,
        annualized_volatility: Decimal | None,
        risk_free_rate: Decimal | None,
    ) -> Decimal | None:
        if (
            annualized_return is None
            or annualized_volatility is None
            or annualized_volatility == 0
        ):
            return None

        risk_free_decimal = (
            (
                risk_free_rate
                if risk_free_rate is not None
                else Decimal("0")
            )
            / Decimal("100")
        )

        return (
            annualized_return
            - risk_free_decimal
        ) / annualized_volatility

    @staticmethod
    def _calculate_maximum_drawdown(
        performance_factors: tuple[Decimal, ...],
    ) -> Decimal:
        index_value = Decimal("1")
        peak_value = Decimal("1")
        maximum_drawdown = Decimal("0")

        for factor in performance_factors:
            index_value *= factor

            if index_value > peak_value:
                peak_value = index_value

            drawdown = (
                Decimal("1")
                - (
                    index_value
                    / peak_value
                )
            )

            if drawdown > maximum_drawdown:
                maximum_drawdown = drawdown

        return maximum_drawdown

    @staticmethod
    def _calculate_value_at_risk(
        *,
        daily_returns: tuple[Decimal, ...],
        final_value: Decimal,
        confidence: Decimal,
    ) -> Decimal | None:
        if len(daily_returns) < 2:
            return None

        tail_probability = (
            Decimal("1")
            - confidence
        )

        percentile_return = (
            HistoricalMetricsCalculator
            ._linear_percentile(
                values=daily_returns,
                percentile=tail_probability,
            )
        )

        loss_rate = max(
            Decimal("0"),
            -percentile_return,
        )

        return (
            loss_rate
            * final_value
        )

    @staticmethod
    def _linear_percentile(
        *,
        values: tuple[Decimal, ...],
        percentile: Decimal,
    ) -> Decimal:
        if not values:
            raise ValueError(
                "No existen valores para calcular "
                "el percentil"
            )

        if not (
            Decimal("0")
            <= percentile
            <= Decimal("1")
        ):
            raise ValueError(
                "El percentil debe estar entre 0 y 1"
            )

        ordered = tuple(
            sorted(values)
        )

        if len(ordered) == 1:
            return ordered[0]

        position = (
            Decimal(len(ordered) - 1)
            * percentile
        )

        lower_index = int(
            position
            .to_integral_value(
                rounding="ROUND_FLOOR"
            )
        )

        upper_index = min(
            lower_index + 1,
            len(ordered) - 1,
        )

        fraction = (
            position
            - Decimal(lower_index)
        )

        lower_value = ordered[lower_index]
        upper_value = ordered[upper_index]

        return (
            lower_value
            + (
                upper_value
                - lower_value
            )
            * fraction
        )