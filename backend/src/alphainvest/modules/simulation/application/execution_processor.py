from uuid import UUID

from alphainvest.modules.simulation.application.historical_data_service import (
    HistoricalDataService,
)
from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
)
from alphainvest.modules.simulation.domain.exceptions import (
    SimulationExecutionNotFoundError,
    SimulationExecutionUnavailableError,
)
from alphainvest.modules.simulation.domain.historical import (
    HistoricalSimulationInput,
)
from alphainvest.modules.simulation.domain.historical_asset_results import (
    HistoricalAssetResultCalculator,
)
from alphainvest.modules.simulation.domain.historical_calendar import (
    HistoricalCalendarAligner,
)
from alphainvest.modules.simulation.domain.historical_engine import (
    HistoricalSimulationEngine,
)
from alphainvest.modules.simulation.infrastructure.models import (
    SimulationResultModel,
)
from alphainvest.modules.simulation.infrastructure.repository import (
    SimulationRepository,
)


class HistoricalExecutionProcessor:
    """Procesa y persiste una ejecución histórica pendiente."""

    def __init__(
        self,
        *,
        repository: SimulationRepository,
        historical_data_service: HistoricalDataService,
    ) -> None:
        self._repository = repository
        self._historical_data_service = (
            historical_data_service
        )

    async def process(
        self,
        *,
        execution_id: UUID,
    ) -> SimulationResultModel:
        execution = (
            await self._repository
            .get_execution_by_id_for_processing(
                execution_id=execution_id
            )
        )

        if execution is None:
            raise SimulationExecutionNotFoundError(
                "La ejecución solicitada no existe"
            )

        if execution.estado != "PENDIENTE":
            raise SimulationExecutionUnavailableError(
                "Solo pueden procesarse ejecuciones "
                "en estado PENDIENTE"
            )

        configuration = execution.configuracion

        if configuration.tipo_simulacion != "HISTORICA":
            raise SimulationExecutionUnavailableError(
                "El procesador histórico solo admite "
                "configuraciones HISTORICA"
            )

        await self._repository.mark_execution_running(
            execution
        )
        await self._repository.commit()

        try:
            assets = []

            for configuration_asset in (
                configuration.activos
            ):
                historical_asset = (
                    await self._historical_data_service
                    .load_asset_history(
                        asset_id=(
                            configuration_asset.activo_id
                        ),
                        assigned_percentage=(
                            configuration_asset
                            .porcentaje_asignado
                        ),
                        start_date=(
                            configuration.fecha_inicio
                        ),
                        end_date=(
                            configuration.fecha_fin
                        ),
                    )
                )

                assets.append(historical_asset)

            contribution_frequency = (
                ContributionFrequency(
                    configuration.frecuencia_aportacion
                )
                if (
                    configuration.frecuencia_aportacion
                    is not None
                )
                else None
            )

            simulation_input = HistoricalSimulationInput(
                initial_capital=(
                    configuration.capital_inicial
                ),
                currency=configuration.moneda_base,
                requested_start_date=(
                    configuration.fecha_inicio
                ),
                requested_end_date=(
                    configuration.fecha_fin
                ),
                assets=tuple(assets),
                periodic_contribution=(
                    configuration.aportacion_periodica
                ),
                contribution_frequency=(
                    contribution_frequency
                ),
                commission_percentage=(
                    configuration.comision_porcentaje
                ),
                risk_free_rate=(
                    configuration.tasa_libre_riesgo
                ),
            )

            historical_result = (
                HistoricalSimulationEngine.run(
                    simulation_input
                )
            )

            aligned_simulation = (
                HistoricalCalendarAligner.align(
                    simulation_input
                )
            )

            asset_results = (
                HistoricalAssetResultCalculator
                .calculate(
                    simulation=aligned_simulation,
                    initial_portfolio=(
                        historical_result
                        .initial_portfolio
                    ),
                    contribution_plan=(
                        historical_result
                        .contribution_plan
                    ),
                    evolution=(
                        historical_result.evolution
                    ),
                )
            )

            persisted_result = (
                await self._repository.create_result(
                    execution_id=execution.id,
                    initial_capital=(
                        historical_result.initial_capital
                    ),
                    total_contributions=(
                        historical_result
                        .total_contributions
                    ),
                    final_capital=(
                        historical_result.final_capital
                    ),
                    profit_loss=(
                        historical_result.profit_loss
                    ),
                    total_return_percentage=(
                        historical_result.metrics
                        .total_return_percentage
                    ),
                    annualized_return_percentage=(
                        historical_result.metrics
                        .annualized_return_percentage
                    ),
                    annualized_volatility=(
                        historical_result.metrics
                        .annualized_volatility_percentage
                    ),
                    sharpe_ratio=(
                        historical_result.metrics
                        .sharpe_ratio
                    ),
                    maximum_drawdown_percentage=(
                        historical_result.metrics
                        .maximum_drawdown_percentage
                    ),
                    value_at_risk=(
                        historical_result.metrics
                        .value_at_risk
                    ),
                    value_at_risk_confidence=(
                        historical_result.metrics
                        .value_at_risk_confidence
                    ),
                    best_scenario=None,
                    worst_scenario=None,
                    median_scenarios=None,
                    gain_probability=None,
                    currency=(
                        historical_result.currency
                    ),
                    summary={
                        "fecha_inicio_efectiva": (
                            historical_result
                            .effective_start_date
                            .isoformat()
                        ),
                        "fecha_fin_efectiva": (
                            historical_result
                            .effective_end_date
                            .isoformat()
                        ),
                        "comisiones_totales": str(
                            historical_result
                            .total_commissions
                        ),
                    },
                )
            )

            for asset_result in asset_results:
                await self._repository.create_asset_result(
                    result_id=persisted_result.id,
                    asset_id=asset_result.asset_id,
                    assigned_percentage=(
                        asset_result
                        .assigned_percentage
                    ),
                    allocated_capital=(
                        asset_result
                        .allocated_capital
                    ),
                    initial_quantity=(
                        asset_result.initial_quantity
                    ),
                    initial_price=(
                        asset_result.initial_price
                    ),
                    final_price=(
                        asset_result.final_price
                    ),
                    final_value=(
                        asset_result.final_value
                    ),
                    profit_loss=(
                        asset_result.profit_loss
                    ),
                    return_percentage=(
                        asset_result.return_percentage
                    ),
                    volatility=(
                        asset_result
                        .volatility_percentage
                    ),
                    maximum_drawdown_percentage=(
                        asset_result
                        .maximum_drawdown_percentage
                    ),
                    detail={
                        "aportaciones_totales": str(
                            asset_result
                            .total_contributions
                        ),
                        "cantidad_final": str(
                            asset_result.final_quantity
                        ),
                    },
                )

            await self._repository.mark_execution_completed(
                execution
            )

            await self._repository.commit()

            return persisted_result

        except Exception as error:
            await self._repository.rollback()

            failed_execution = (
                await self._repository
                .get_execution_by_id_for_processing(
                    execution_id=execution_id
                )
            )

            if failed_execution is not None:
                error_message = (
                    str(error).strip()
                    or error.__class__.__name__
                )

                await self._repository.mark_execution_failed(
                    failed_execution,
                    error_message=error_message,
                )

                await self._repository.commit()

            raise