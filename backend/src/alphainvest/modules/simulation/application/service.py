from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.portfolio.infrastructure.repository import (
    PortfolioRepository,
)
from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
    SimulationConfigurationStatus,
    SimulationExecutionStatus,
    SimulationType,
)
from alphainvest.modules.simulation.domain.exceptions import (
    SimulationAssetNotFoundError,
    SimulationAssetUnavailableError,
    SimulationConfigurationAssetAlreadyExistsError,
    SimulationConfigurationAssetNotFoundError,
    SimulationConfigurationNameAlreadyExistsError,
    SimulationConfigurationNotFoundError,
    SimulationConfigurationUnavailableError,
    SimulationDistributionInvalidError,
    SimulationExecutionAlreadyActiveError,
    SimulationExecutionNotFoundError,
    SimulationExecutionUnavailableError,
    SimulationModelVersionNotFoundError,
    SimulationModelVersionUnavailableError,
    SimulationPortfolioNotFoundError,
)
from alphainvest.modules.simulation.infrastructure.models import (
    SimulationConfigurationAssetModel,
    SimulationConfigurationModel,
    SimulationExecutionModel,
)
from alphainvest.modules.simulation.infrastructure.repository import (
    SimulationRepository,
)
from alphainvest.modules.simulation.presentation.schemas import (
    SimulationConfigurationArchiveResponse,
    SimulationConfigurationAssetCreateRequest,
    SimulationConfigurationAssetListResponse,
    SimulationConfigurationAssetResponse,
    SimulationConfigurationAssetUpdateRequest,
    SimulationConfigurationCreateRequest,
    SimulationConfigurationListResponse,
    SimulationConfigurationReadyResponse,
    SimulationConfigurationResponse,
    SimulationConfigurationUpdateRequest,
    SimulationDistributionStatusResponse,
    SimulationExecutionCancelResponse,
    SimulationExecutionCreateRequest,
    SimulationExecutionListResponse,
    SimulationExecutionResponse,
    SimulationResultResponse,
)


class SimulationService:
    """Casos de uso del módulo Simulation."""

    def __init__(
        self,
        *,
        repository: SimulationRepository,
        portfolio_repository: PortfolioRepository,
        market_repository: MarketRepository,
        ai_repository: AIRepository,
    ) -> None:
        self._repository = repository
        self._portfolio_repository = (
            portfolio_repository
        )
        self._market_repository = market_repository
        self._ai_repository = ai_repository

    async def create_configuration(
        self,
        *,
        user_id: UUID,
        request: SimulationConfigurationCreateRequest,
    ) -> SimulationConfigurationResponse:
        existing = (
            await self._repository
            .get_configuration_by_name_for_user(
                user_id=user_id,
                name=request.nombre,
            )
        )

        if existing is not None:
            raise (
                SimulationConfigurationNameAlreadyExistsError(
                    "Ya existe una configuración "
                    "con ese nombre"
                )
            )

        await self._validate_optional_portfolio(
            portfolio_id=request.portafolio_id,
            user_id=user_id,
        )

        try:
            configuration = (
                await self._repository
                .create_configuration(
                    user_id=user_id,
                    portfolio_id=request.portafolio_id,
                    name=request.nombre,
                    description=request.descripcion,
                    simulation_type=(
                        request.tipo_simulacion.value
                    ),
                    initial_capital=(
                        request.capital_inicial
                    ),
                    base_currency=request.moneda_base,
                    start_date=request.fecha_inicio,
                    end_date=request.fecha_fin,
                    periodic_contribution=(
                        request.aportacion_periodica
                    ),
                    contribution_frequency=(
                        request.frecuencia_aportacion.value
                        if (
                            request.frecuencia_aportacion
                            is not None
                        )
                        else None
                    ),
                    commission_percentage=(
                        request.comision_porcentaje
                    ),
                    annual_inflation=(
                        request.inflacion_anual
                    ),
                    risk_free_rate=(
                        request.tasa_libre_riesgo
                    ),
                    scenario_count=(
                        request.numero_escenarios
                    ),
                    random_seed=(
                        request.semilla_aleatoria
                    ),
                    parameters=request.parametros,
                )
            )

            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        return (
            SimulationConfigurationResponse
            .model_validate(configuration)
        )

    async def list_configurations(
        self,
        *,
        user_id: UUID,
        status: (
            SimulationConfigurationStatus | None
        ),
        limit: int,
        offset: int,
    ) -> SimulationConfigurationListResponse:
        configurations, total = (
            await self._repository
            .list_configurations_for_user(
                user_id=user_id,
                status=(
                    status.value
                    if status is not None
                    else None
                ),
                limit=limit,
                offset=offset,
            )
        )

        return SimulationConfigurationListResponse(
            items=[
                SimulationConfigurationResponse
                .model_validate(configuration)
                for configuration in configurations
            ],
            total=total,
            limit=limit,
            offset=offset,
            estado=status,
        )

    async def get_configuration(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationConfigurationResponse:
        configuration = (
            await self._get_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        return (
            SimulationConfigurationResponse
            .model_validate(configuration)
        )

    async def update_configuration(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
        request: SimulationConfigurationUpdateRequest,
    ) -> SimulationConfigurationResponse:
        configuration = (
            await self._get_draft_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        if (
            "nombre" in request.model_fields_set
            and request.nombre is not None
            and (
                request.nombre.strip().lower()
                != configuration.nombre.strip().lower()
            )
        ):
            existing = (
                await self._repository
                .get_configuration_by_name_for_user(
                    user_id=user_id,
                    name=request.nombre,
                )
            )

            if (
                existing is not None
                and existing.id != configuration.id
            ):
                raise (
                    SimulationConfigurationNameAlreadyExistsError(
                        "Ya existe una configuración "
                        "con ese nombre"
                    )
                )

        if "portafolio_id" in request.model_fields_set:
            await self._validate_optional_portfolio(
                portfolio_id=request.portafolio_id,
                user_id=user_id,
            )

        final_start_date = (
            request.fecha_inicio
            if request.fecha_inicio is not None
            else configuration.fecha_inicio
        )
        final_end_date = (
            request.fecha_fin
            if request.fecha_fin is not None
            else configuration.fecha_fin
        )
        final_contribution = (
            request.aportacion_periodica
            if request.aportacion_periodica is not None
            else configuration.aportacion_periodica
        )
        final_frequency = (
            request.frecuencia_aportacion
            if (
                "frecuencia_aportacion"
                in request.model_fields_set
            )
            else configuration.frecuencia_aportacion
        )
        final_simulation_type = (
            request.tipo_simulacion
            if request.tipo_simulacion is not None
            else SimulationType(
                configuration.tipo_simulacion
            )
        )
        final_scenario_count = (
            request.numero_escenarios
            if request.numero_escenarios is not None
            else configuration.numero_escenarios
        )

        self._validate_final_configuration(
            start_date=final_start_date,
            end_date=final_end_date,
            periodic_contribution=(
                final_contribution
            ),
            contribution_frequency=(
                final_frequency.value
                if isinstance(
                    final_frequency,
                    ContributionFrequency,
                )
                else final_frequency
            ),
            simulation_type=(
                final_simulation_type
            ),
            scenario_count=final_scenario_count,
        )

        try:
            updated = (
                await self._repository
                .update_configuration(
                    configuration,
                    portfolio_id=(
                        request.portafolio_id
                    ),
                    portfolio_was_sent=(
                        "portafolio_id"
                        in request.model_fields_set
                    ),
                    name=request.nombre,
                    description=(
                        request.descripcion
                    ),
                    description_was_sent=(
                        "descripcion"
                        in request.model_fields_set
                    ),
                    simulation_type=(
                        request.tipo_simulacion.value
                        if (
                            request.tipo_simulacion
                            is not None
                        )
                        else None
                    ),
                    initial_capital=(
                        request.capital_inicial
                    ),
                    base_currency=(
                        request.moneda_base
                    ),
                    start_date=(
                        request.fecha_inicio
                    ),
                    end_date=request.fecha_fin,
                    periodic_contribution=(
                        request.aportacion_periodica
                    ),
                    contribution_frequency=(
                        request.frecuencia_aportacion.value
                        if (
                            request.frecuencia_aportacion
                            is not None
                        )
                        else None
                    ),
                    contribution_frequency_was_sent=(
                        "frecuencia_aportacion"
                        in request.model_fields_set
                    ),
                    commission_percentage=(
                        request.comision_porcentaje
                    ),
                    annual_inflation=(
                        request.inflacion_anual
                    ),
                    annual_inflation_was_sent=(
                        "inflacion_anual"
                        in request.model_fields_set
                    ),
                    risk_free_rate=(
                        request.tasa_libre_riesgo
                    ),
                    risk_free_rate_was_sent=(
                        "tasa_libre_riesgo"
                        in request.model_fields_set
                    ),
                    scenario_count=(
                        request.numero_escenarios
                    ),
                    random_seed=(
                        request.semilla_aleatoria
                    ),
                    random_seed_was_sent=(
                        "semilla_aleatoria"
                        in request.model_fields_set
                    ),
                    parameters=request.parametros,
                    parameters_were_sent=(
                        "parametros"
                        in request.model_fields_set
                    ),
                )
            )

            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        return (
            SimulationConfigurationResponse
            .model_validate(updated)
        )

    async def archive_configuration(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationConfigurationArchiveResponse:
        configuration = (
            await self._get_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        if (
            configuration.estado
            == SimulationConfigurationStatus.ARCHIVED.value
        ):
            raise (
                SimulationConfigurationUnavailableError(
                    "La configuración ya está archivada"
                )
            )

        try:
            archived = (
                await self._repository
                .archive_configuration(
                    configuration
                )
            )
            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        return SimulationConfigurationArchiveResponse(
            id=archived.id,
            estado=(
                SimulationConfigurationStatus(
                    archived.estado
                )
            ),
        )

    async def add_configuration_asset(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
        request: SimulationConfigurationAssetCreateRequest,
    ) -> SimulationConfigurationAssetResponse:
        configuration = (
            await self._get_draft_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        asset = await self._market_repository.get_asset(
            request.activo_id
        )

        if asset is None:
            raise SimulationAssetNotFoundError(
                "El activo solicitado no existe"
            )

        if asset.estado != "ACTIVO":
            raise SimulationAssetUnavailableError(
                "El activo no está disponible "
                "para simulaciones"
            )

        existing_asset = (
            await self._repository
            .get_configuration_asset(
                configuration_id=configuration.id,
                asset_id=request.activo_id,
            )
        )

        if existing_asset is not None:
            raise (
                SimulationConfigurationAssetAlreadyExistsError(
                    "El activo ya pertenece "
                    "a la configuración"
                )
            )

        existing_order = (
            await self._repository
            .get_configuration_asset_by_order(
                configuration_id=configuration.id,
                order=request.orden,
            )
        )

        if existing_order is not None:
            raise (
                SimulationConfigurationAssetAlreadyExistsError(
                    "El orden ya está ocupado "
                    "por otro activo"
                )
            )

        try:
            configuration_asset = (
                await self._repository
                .create_configuration_asset(
                    configuration_id=configuration.id,
                    asset_id=request.activo_id,
                    assigned_percentage=(
                        request.porcentaje_asignado
                    ),
                    initial_amount=(
                        request.monto_inicial
                    ),
                    initial_price=(
                        request.precio_inicial
                    ),
                    order=request.orden,
                    parameters=request.parametros,
                )
            )

            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        return (
            SimulationConfigurationAssetResponse
            .model_validate(configuration_asset)
        )

    async def list_configuration_assets(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationConfigurationAssetListResponse:
        configuration = await self._get_configuration(
            configuration_id=configuration_id,
            user_id=user_id,
        )

        assets = (
            await self._repository
            .list_configuration_assets(
                configuration_id=configuration.id,
            )
        )

        distribution_data = (
            await self._repository
            .get_distribution_status(
                configuration_id=configuration.id,
            )
        )

        return SimulationConfigurationAssetListResponse(
            configuracion_id=configuration.id,
            items=[
                SimulationConfigurationAssetResponse
                .model_validate(configuration_asset)
                for configuration_asset in assets
            ],
            total=len(assets),
            porcentaje_total=Decimal(
                str(
                    distribution_data[
                        "porcentaje_total"
                    ]
                )
            ),
            monto_total=Decimal(
                str(
                    distribution_data[
                        "monto_total"
                    ]
                )
            ),
            distribucion_valida=bool(
                distribution_data[
                    "distribucion_valida"
                ]
            ),
        )

    async def update_configuration_asset(
        self,
        *,
        configuration_id: UUID,
        asset_id: UUID,
        user_id: UUID,
        request: SimulationConfigurationAssetUpdateRequest,
    ) -> SimulationConfigurationAssetResponse:
        configuration = (
            await self._get_draft_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        configuration_asset = (
            await self._get_configuration_asset(
                configuration_id=configuration.id,
                asset_id=asset_id,
            )
        )

        if (
            request.orden is not None
            and request.orden
            != configuration_asset.orden
        ):
            existing_order = (
                await self._repository
                .get_configuration_asset_by_order(
                    configuration_id=(
                        configuration.id
                    ),
                    order=request.orden,
                )
            )

            if existing_order is not None:
                raise (
                    SimulationConfigurationAssetAlreadyExistsError(
                        "El orden ya está ocupado "
                        "por otro activo"
                    )
                )

        try:
            updated = (
                await self._repository
                .update_configuration_asset(
                    configuration_asset,
                    assigned_percentage=(
                        request.porcentaje_asignado
                    ),
                    initial_amount=(
                        request.monto_inicial
                    ),
                    initial_amount_was_sent=(
                        "monto_inicial"
                        in request.model_fields_set
                    ),
                    initial_price=(
                        request.precio_inicial
                    ),
                    initial_price_was_sent=(
                        "precio_inicial"
                        in request.model_fields_set
                    ),
                    order=request.orden,
                    parameters=request.parametros,
                    parameters_were_sent=(
                        "parametros"
                        in request.model_fields_set
                    ),
                )
            )

            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        return (
            SimulationConfigurationAssetResponse
            .model_validate(updated)
        )

    async def delete_configuration_asset(
        self,
        *,
        configuration_id: UUID,
        asset_id: UUID,
        user_id: UUID,
    ) -> None:
        configuration = (
            await self._get_draft_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        configuration_asset = (
            await self._get_configuration_asset(
                configuration_id=configuration.id,
                asset_id=asset_id,
            )
        )

        try:
            await self._repository.delete_configuration_asset(
                configuration_asset
            )
            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

    async def get_distribution_status(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationDistributionStatusResponse:
        configuration = await self._get_configuration(
            configuration_id=configuration_id,
            user_id=user_id,
        )

        distribution_data = (
            await self._repository
            .get_distribution_status(
                configuration_id=configuration.id,
            )
        )

        return self._build_distribution_response(
            distribution_data
        )

    async def mark_configuration_ready(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationConfigurationReadyResponse:
        configuration = (
            await self._get_draft_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        distribution_data = (
            await self._repository
            .get_distribution_status(
                configuration_id=configuration.id,
            )
        )

        if not bool(
            distribution_data["distribucion_valida"]
        ):
            raise SimulationDistributionInvalidError(
                "La configuración debe incluir "
                "al menos un activo y sus porcentajes "
                "deben sumar 100"
            )

        try:
            ready_configuration = (
                await self._repository
                .mark_configuration_ready(
                    configuration
                )
            )
            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        refreshed_distribution = (
            await self._repository
            .get_distribution_status(
                configuration_id=(
                    ready_configuration.id
                ),
            )
        )

        return SimulationConfigurationReadyResponse(
            id=ready_configuration.id,
            estado=SimulationConfigurationStatus(
                ready_configuration.estado
            ),
            distribucion=(
                self._build_distribution_response(
                    refreshed_distribution
                )
            ),
        )

    async def create_execution(
        self,
        *,
        user_id: UUID,
        request: SimulationExecutionCreateRequest,
    ) -> SimulationExecutionResponse:
        configuration = await self._get_configuration(
            configuration_id=request.configuracion_id,
            user_id=user_id,
        )

        if (
            configuration.estado
            != SimulationConfigurationStatus.READY.value
        ):
            raise (
                SimulationConfigurationUnavailableError(
                    "La configuración debe estar "
                    "en estado LISTA para ejecutarse"
                )
            )

        distribution_data = (
            await self._repository
            .get_distribution_status(
                configuration_id=configuration.id,
            )
        )

        if not bool(
            distribution_data["distribucion_valida"]
        ):
            raise SimulationDistributionInvalidError(
                "La configuración no tiene una "
                "distribución válida"
            )

        active_execution = (
            await self._repository
            .get_active_execution_for_configuration(
                configuration_id=configuration.id,
            )
        )

        if active_execution is not None:
            raise SimulationExecutionAlreadyActiveError(
                "La configuración ya tiene una "
                "ejecución activa"
            )

        await self._validate_optional_model_version(
            model_version_id=(
                request.version_modelo_id
            )
        )

        try:
            execution = (
                await self._repository.create_execution(
                    configuration_id=configuration.id,
                    user_id=user_id,
                    model_version_id=(
                        request.version_modelo_id
                    ),
                    execution_parameters=(
                        request.parametros_ejecucion
                    ),
                )
            )

            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        return SimulationExecutionResponse.model_validate(
            execution
        )

    async def list_executions(
        self,
        *,
        user_id: UUID,
        status: SimulationExecutionStatus | None,
        configuration_id: UUID | None,
        limit: int,
        offset: int,
    ) -> SimulationExecutionListResponse:
        if configuration_id is not None:
            await self._get_configuration(
                configuration_id=configuration_id,
                user_id=user_id,
            )

        executions, total = (
            await self._repository
            .list_executions_for_user(
                user_id=user_id,
                status=(
                    status.value
                    if status is not None
                    else None
                ),
                configuration_id=configuration_id,
                limit=limit,
                offset=offset,
            )
        )

        return SimulationExecutionListResponse(
            items=[
                SimulationExecutionResponse
                .model_validate(execution)
                for execution in executions
            ],
            total=total,
            limit=limit,
            offset=offset,
            estado=status,
            configuracion_id=configuration_id,
        )

    async def get_execution(
        self,
        *,
        execution_id: UUID,
        user_id: UUID,
    ) -> SimulationExecutionResponse:
        execution = await self._get_execution(
            execution_id=execution_id,
            user_id=user_id,
        )

        return SimulationExecutionResponse.model_validate(
            execution
        )

    async def get_result(
        self,
        *,
        execution_id: UUID,
        user_id: UUID,
    ) -> SimulationResultResponse:
        execution = await self._get_execution(
            execution_id=execution_id,
            user_id=user_id,
        )

        if execution.resultado is None:
            raise SimulationExecutionUnavailableError(
                "La ejecución todavía no tiene "
                "resultados disponibles"
            )

        return SimulationResultResponse.model_validate(
            execution.resultado
        )

    async def cancel_execution(
        self,
        *,
        execution_id: UUID,
        user_id: UUID,
    ) -> SimulationExecutionCancelResponse:
        execution = await self._get_execution(
            execution_id=execution_id,
            user_id=user_id,
        )

        if execution.estado not in {
            "PENDIENTE",
            "EJECUTANDO",
        }:
            raise SimulationExecutionUnavailableError(
                "Solo pueden cancelarse ejecuciones "
                "PENDIENTES o EJECUTANDO"
            )

        try:
            cancelled = (
                await self._repository.cancel_execution(
                    execution
                )
            )
            await self._repository.commit()
        except Exception:
            await self._repository.rollback()
            raise

        if cancelled.fecha_fin is None:
            raise RuntimeError(
                "PostgreSQL no registró la fecha "
                "final de la cancelación"
            )

        return SimulationExecutionCancelResponse(
            id=cancelled.id,
            estado=SimulationExecutionStatus(
                cancelled.estado
            ),
            porcentaje_progreso=(
                cancelled.porcentaje_progreso
            ),
            fecha_inicio=cancelled.fecha_inicio,
            fecha_fin=cancelled.fecha_fin,
        )

    async def _get_execution(
        self,
        *,
        execution_id: UUID,
        user_id: UUID,
    ) -> SimulationExecutionModel:
        execution = (
            await self._repository
            .get_execution_by_id_for_user(
                execution_id=execution_id,
                user_id=user_id,
            )
        )

        if execution is None:
            raise SimulationExecutionNotFoundError(
                "La ejecución solicitada no existe"
            )

        return execution

    async def _get_configuration(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationConfigurationModel:
        configuration = (
            await self._repository
            .get_configuration_by_id_for_user(
                configuration_id=configuration_id,
                user_id=user_id,
            )
        )

        if configuration is None:
            raise SimulationConfigurationNotFoundError(
                "La configuración solicitada no existe"
            )

        return configuration

    async def _get_draft_configuration(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationConfigurationModel:
        configuration = await self._get_configuration(
            configuration_id=configuration_id,
            user_id=user_id,
        )

        if (
            configuration.estado
            != SimulationConfigurationStatus.DRAFT.value
        ):
            raise (
                SimulationConfigurationUnavailableError(
                    "Solo pueden modificarse "
                    "configuraciones en estado BORRADOR"
                )
            )

        return configuration

    async def _get_configuration_asset(
        self,
        *,
        configuration_id: UUID,
        asset_id: UUID,
    ) -> SimulationConfigurationAssetModel:
        configuration_asset = (
            await self._repository
            .get_configuration_asset(
                configuration_id=configuration_id,
                asset_id=asset_id,
            )
        )

        if configuration_asset is None:
            raise (
                SimulationConfigurationAssetNotFoundError(
                    "El activo no pertenece "
                    "a la configuración"
                )
            )

        return configuration_asset

    async def _validate_optional_model_version(
        self,
        *,
        model_version_id: UUID | None,
    ) -> None:
        if model_version_id is None:
            return

        version = await self._ai_repository.get_model_version(
            model_version_id
        )

        if version is None:
            raise SimulationModelVersionNotFoundError(
                "La versión de modelo solicitada "
                "no existe"
            )

        active_version = (
            await self._ai_repository
            .get_active_model_version(
                model_version_id
            )
        )

        if active_version is None:
            raise SimulationModelVersionUnavailableError(
                "La versión de modelo no está activa"
            )

    async def _validate_optional_portfolio(
        self,
        *,
        portfolio_id: UUID | None,
        user_id: UUID,
    ) -> None:
        if portfolio_id is None:
            return

        portfolio = (
            await self._portfolio_repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=user_id,
            )
        )

        if portfolio is None:
            raise SimulationPortfolioNotFoundError(
                "El portafolio asociado no existe"
            )

    @staticmethod
    def _build_distribution_response(
        distribution_data: dict[str, object],
    ) -> SimulationDistributionStatusResponse:
        return SimulationDistributionStatusResponse(
            configuracion_id=UUID(
                str(
                    distribution_data[
                        "configuracion_id"
                    ]
                )
            ),
            estado=SimulationConfigurationStatus(
                str(distribution_data["estado"])
            ),
            cantidad_activos=int(
                str(
                    distribution_data[
                        "cantidad_activos"
                    ]
                )
            ),
            porcentaje_total=Decimal(
                str(
                    distribution_data[
                        "porcentaje_total"
                    ]
                )
            ),
            monto_total=Decimal(
                str(
                    distribution_data[
                        "monto_total"
                    ]
                )
            ),
            capital_inicial=Decimal(
                str(
                    distribution_data[
                        "capital_inicial"
                    ]
                )
            ),
            distribucion_valida=bool(
                distribution_data[
                    "distribucion_valida"
                ]
            ),
        )

    @staticmethod
    def _validate_final_configuration(
        *,
        start_date: date,
        end_date: date,
        periodic_contribution: Decimal,
        contribution_frequency: str | None,
        simulation_type: SimulationType,
        scenario_count: int,
    ) -> None:
        if end_date <= start_date:
            raise ValueError(
                "La fecha final debe ser posterior "
                "a la fecha inicial"
            )

        if periodic_contribution == 0:
            if contribution_frequency is not None:
                raise ValueError(
                    "No debe indicar una frecuencia "
                    "cuando la aportación es cero"
                )
        elif contribution_frequency is None:
            raise ValueError(
                "Debe indicar la frecuencia de "
                "la aportación periódica"
            )

        if (
            simulation_type
            == SimulationType.MONTE_CARLO
            and scenario_count <= 1
        ):
            raise ValueError(
                "Monte Carlo requiere más de "
                "un escenario"
            )