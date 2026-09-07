from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.simulation.infrastructure.models import (
    SimulationAssetResultModel,
    SimulationConfigurationAssetModel,
    SimulationConfigurationModel,
    SimulationExecutionModel,
    SimulationResultModel,
)


class SimulationRepository:
    """Acceso a datos del módulo Simulation."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_configuration_by_id_for_user(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
    ) -> SimulationConfigurationModel | None:
        statement = (
            select(SimulationConfigurationModel)
            .where(
                SimulationConfigurationModel.id
                == configuration_id,
                SimulationConfigurationModel.usuario_id
                == user_id,
            )
            .options(
                selectinload(
                    SimulationConfigurationModel.activos
                ),
                selectinload(
                    SimulationConfigurationModel.ejecuciones
                ),
            )
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_configuration_by_name_for_user(
        self,
        *,
        user_id: UUID,
        name: str,
    ) -> SimulationConfigurationModel | None:
        statement = select(
            SimulationConfigurationModel
        ).where(
            SimulationConfigurationModel.usuario_id
            == user_id,
            func.lower(
                SimulationConfigurationModel.nombre
            )
            == name.strip().lower(),
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_configurations_for_user(
        self,
        *,
        user_id: UUID,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[
        list[SimulationConfigurationModel],
        int,
    ]:
        filters = [
            SimulationConfigurationModel.usuario_id
            == user_id
        ]

        if status is not None:
            filters.append(
                SimulationConfigurationModel.estado
                == status
            )

        statement = (
            select(SimulationConfigurationModel)
            .where(*filters)
            .order_by(
                SimulationConfigurationModel
                .fecha_creacion
                .desc(),
                SimulationConfigurationModel.id.asc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(
                func.count(
                    SimulationConfigurationModel.id
                )
            )
            .where(*filters)
        )

        result = await self._session.execute(
            statement
        )
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def create_configuration(
        self,
        *,
        user_id: UUID,
        portfolio_id: UUID | None,
        name: str,
        description: str | None,
        simulation_type: str,
        initial_capital: Decimal,
        base_currency: str,
        start_date: date,
        end_date: date,
        periodic_contribution: Decimal,
        contribution_frequency: str | None,
        commission_percentage: Decimal,
        annual_inflation: Decimal | None,
        risk_free_rate: Decimal | None,
        scenario_count: int,
        random_seed: int | None,
        parameters: dict[str, Any] | None,
    ) -> SimulationConfigurationModel:
        configuration = (
            SimulationConfigurationModel(
                usuario_id=user_id,
                portafolio_id=portfolio_id,
                nombre=name,
                descripcion=description,
                tipo_simulacion=simulation_type,
                capital_inicial=initial_capital,
                moneda_base=base_currency,
                fecha_inicio=start_date,
                fecha_fin=end_date,
                aportacion_periodica=(
                    periodic_contribution
                ),
                frecuencia_aportacion=(
                    contribution_frequency
                ),
                comision_porcentaje=(
                    commission_percentage
                ),
                inflacion_anual=annual_inflation,
                tasa_libre_riesgo=risk_free_rate,
                numero_escenarios=scenario_count,
                semilla_aleatoria=random_seed,
                parametros=parameters,
                estado="BORRADOR",
            )
        )

        self._session.add(configuration)
        await self._session.flush()
        await self._session.refresh(configuration)

        return configuration

    async def update_configuration(
        self,
        configuration: SimulationConfigurationModel,
        *,
        portfolio_id: UUID | None,
        portfolio_was_sent: bool,
        name: str | None,
        description: str | None,
        description_was_sent: bool,
        simulation_type: str | None,
        initial_capital: Decimal | None,
        base_currency: str | None,
        start_date: date | None,
        end_date: date | None,
        periodic_contribution: Decimal | None,
        contribution_frequency: str | None,
        contribution_frequency_was_sent: bool,
        commission_percentage: Decimal | None,
        annual_inflation: Decimal | None,
        annual_inflation_was_sent: bool,
        risk_free_rate: Decimal | None,
        risk_free_rate_was_sent: bool,
        scenario_count: int | None,
        random_seed: int | None,
        random_seed_was_sent: bool,
        parameters: dict[str, Any] | None,
        parameters_were_sent: bool,
    ) -> SimulationConfigurationModel:
        if portfolio_was_sent:
            configuration.portafolio_id = portfolio_id

        if name is not None:
            configuration.nombre = name

        if description_was_sent:
            configuration.descripcion = description

        if simulation_type is not None:
            configuration.tipo_simulacion = (
                simulation_type
            )

        if initial_capital is not None:
            configuration.capital_inicial = (
                initial_capital
            )

        if base_currency is not None:
            configuration.moneda_base = (
                base_currency
            )

        if start_date is not None:
            configuration.fecha_inicio = (
                start_date
            )

        if end_date is not None:
            configuration.fecha_fin = end_date

        if periodic_contribution is not None:
            configuration.aportacion_periodica = (
                periodic_contribution
            )

        if contribution_frequency_was_sent:
            configuration.frecuencia_aportacion = (
                contribution_frequency
            )

        if commission_percentage is not None:
            configuration.comision_porcentaje = (
                commission_percentage
            )

        if annual_inflation_was_sent:
            configuration.inflacion_anual = (
                annual_inflation
            )

        if risk_free_rate_was_sent:
            configuration.tasa_libre_riesgo = (
                risk_free_rate
            )

        if scenario_count is not None:
            configuration.numero_escenarios = (
                scenario_count
            )

        if random_seed_was_sent:
            configuration.semilla_aleatoria = (
                random_seed
            )

        if parameters_were_sent:
            configuration.parametros = parameters

        await self._session.flush()
        await self._session.refresh(configuration)

        return configuration

    async def archive_configuration(
        self,
        configuration: SimulationConfigurationModel,
    ) -> SimulationConfigurationModel:
        configuration.estado = "ARCHIVADA"

        await self._session.flush()
        await self._session.refresh(configuration)

        return configuration

    async def get_configuration_asset(
        self,
        *,
        configuration_id: UUID,
        asset_id: UUID,
    ) -> SimulationConfigurationAssetModel | None:
        statement = (
            select(
                SimulationConfigurationAssetModel
            )
            .where(
                SimulationConfigurationAssetModel
                .configuracion_id
                == configuration_id,
                SimulationConfigurationAssetModel
                .activo_id
                == asset_id,
            )
            .options(
                selectinload(
                    SimulationConfigurationAssetModel
                    .activo
                )
            )
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_configuration_asset_by_order(
        self,
        *,
        configuration_id: UUID,
        order: int,
    ) -> SimulationConfigurationAssetModel | None:
        statement = select(
            SimulationConfigurationAssetModel
        ).where(
            SimulationConfigurationAssetModel
            .configuracion_id
            == configuration_id,
            SimulationConfigurationAssetModel
            .orden
            == order,
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_configuration_assets(
        self,
        *,
        configuration_id: UUID,
    ) -> list[
        SimulationConfigurationAssetModel
    ]:
        statement = (
            select(
                SimulationConfigurationAssetModel
            )
            .where(
                SimulationConfigurationAssetModel
                .configuracion_id
                == configuration_id
            )
            .options(
                selectinload(
                    SimulationConfigurationAssetModel
                    .activo
                )
            )
            .order_by(
                SimulationConfigurationAssetModel
                .orden
                .asc(),
                SimulationConfigurationAssetModel
                .activo_id
                .asc(),
            )
        )

        result = await self._session.execute(
            statement
        )

        return list(result.scalars().all())

    async def create_configuration_asset(
        self,
        *,
        configuration_id: UUID,
        asset_id: UUID,
        assigned_percentage: Decimal,
        initial_amount: Decimal | None,
        initial_price: Decimal | None,
        order: int,
        parameters: dict[str, Any] | None,
    ) -> SimulationConfigurationAssetModel:
        configuration_asset = (
            SimulationConfigurationAssetModel(
                configuracion_id=configuration_id,
                activo_id=asset_id,
                porcentaje_asignado=(
                    assigned_percentage
                ),
                monto_inicial=initial_amount,
                precio_inicial=initial_price,
                orden=order,
                parametros=parameters,
            )
        )

        self._session.add(configuration_asset)
        await self._session.flush()
        await self._session.refresh(
            configuration_asset
        )

        return configuration_asset

    async def update_configuration_asset(
        self,
        configuration_asset: (
            SimulationConfigurationAssetModel
        ),
        *,
        assigned_percentage: Decimal | None,
        initial_amount: Decimal | None,
        initial_amount_was_sent: bool,
        initial_price: Decimal | None,
        initial_price_was_sent: bool,
        order: int | None,
        parameters: dict[str, Any] | None,
        parameters_were_sent: bool,
    ) -> SimulationConfigurationAssetModel:
        if assigned_percentage is not None:
            configuration_asset.porcentaje_asignado = (
                assigned_percentage
            )

        if initial_amount_was_sent:
            configuration_asset.monto_inicial = (
                initial_amount
            )

        if initial_price_was_sent:
            configuration_asset.precio_inicial = (
                initial_price
            )

        if order is not None:
            configuration_asset.orden = order

        if parameters_were_sent:
            configuration_asset.parametros = (
                parameters
            )

        await self._session.flush()
        await self._session.refresh(
            configuration_asset
        )

        return configuration_asset

    async def delete_configuration_asset(
        self,
        configuration_asset: (
            SimulationConfigurationAssetModel
        ),
    ) -> None:
        await self._session.delete(
            configuration_asset
        )
        await self._session.flush()

    async def get_distribution_status(
        self,
        *,
        configuration_id: UUID,
    ) -> dict[str, object]:
        statement = text(
            """
            SELECT
                c.id AS configuracion_id,
                c.estado,
                c.capital_inicial,
                COUNT(ca.activo_id)::INTEGER
                    AS cantidad_activos,
                COALESCE(
                    SUM(ca.porcentaje_asignado),
                    0
                ) AS porcentaje_total,
                COALESCE(
                    SUM(ca.monto_inicial),
                    0
                ) AS monto_total,
                simulation.fn_validar_distribucion(
                    c.id
                ) AS distribucion_valida
            FROM simulation.configuraciones AS c
            LEFT JOIN
                simulation.configuracion_activos
                AS ca
                ON ca.configuracion_id = c.id
            WHERE c.id = :configuration_id
            GROUP BY
                c.id,
                c.estado,
                c.capital_inicial
            """
        )

        result = await self._session.execute(
            statement,
            {
                "configuration_id": configuration_id,
            },
        )

        row = result.mappings().one()

        return dict(row)

    async def mark_configuration_ready(
        self,
        configuration: SimulationConfigurationModel,
    ) -> SimulationConfigurationModel:
        configuration.estado = "LISTA"

        await self._session.flush()
        await self._session.refresh(configuration)

        return configuration

    async def get_execution_by_id_for_user(
        self,
        *,
        execution_id: UUID,
        user_id: UUID,
    ) -> SimulationExecutionModel | None:
        statement = (
            select(SimulationExecutionModel)
            .where(
                SimulationExecutionModel.id
                == execution_id,
                SimulationExecutionModel.usuario_id
                == user_id,
            )
            .options(
                selectinload(
                    SimulationExecutionModel.configuracion
                ),
                selectinload(
                    SimulationExecutionModel.resultado
                ),
            )
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_execution_by_id_for_processing(
        self,
        *,
        execution_id: UUID,
    ) -> SimulationExecutionModel | None:
        statement = (
            select(SimulationExecutionModel)
            .where(
                SimulationExecutionModel.id
                == execution_id
            )
            .options(
                selectinload(
                    SimulationExecutionModel.configuracion
                ).selectinload(
                    SimulationConfigurationModel.activos
                ),
                selectinload(
                    SimulationExecutionModel.resultado
                ),
            )
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def list_pending_executions_for_processing(
        self,
        *,
        limit: int,
    ) -> list[SimulationExecutionModel]:
        statement = (
            select(SimulationExecutionModel)
            .join(
                SimulationConfigurationModel,
                (
                    SimulationConfigurationModel.id
                    == SimulationExecutionModel
                    .configuracion_id
                ),
            )
            .where(
                SimulationExecutionModel.estado
                == "PENDIENTE",
                SimulationConfigurationModel
                .tipo_simulacion
                == "HISTORICA",
            )
            .order_by(
                SimulationExecutionModel
                .fecha_solicitud
                .asc(),
                SimulationExecutionModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_executions_for_user(
        self,
        *,
        user_id: UUID,
        status: str | None,
        configuration_id: UUID | None,
        limit: int,
        offset: int,
    ) -> tuple[
        list[SimulationExecutionModel],
        int,
    ]:
        filters = [
            SimulationExecutionModel.usuario_id
            == user_id
        ]

        if status is not None:
            filters.append(
                SimulationExecutionModel.estado
                == status
            )

        if configuration_id is not None:
            filters.append(
                SimulationExecutionModel.configuracion_id
                == configuration_id
            )

        statement = (
            select(SimulationExecutionModel)
            .where(*filters)
            .order_by(
                SimulationExecutionModel
                .fecha_solicitud
                .desc(),
                SimulationExecutionModel.id.asc(),
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(
                func.count(
                    SimulationExecutionModel.id
                )
            )
            .where(*filters)
        )

        result = await self._session.execute(
            statement
        )
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def get_active_execution_for_configuration(
        self,
        *,
        configuration_id: UUID,
    ) -> SimulationExecutionModel | None:
        statement = (
            select(SimulationExecutionModel)
            .where(
                SimulationExecutionModel.configuracion_id
                == configuration_id,
                SimulationExecutionModel.estado.in_(
                    (
                        "PENDIENTE",
                        "EJECUTANDO",
                    )
                ),
            )
            .order_by(
                SimulationExecutionModel
                .fecha_solicitud
                .desc(),
                SimulationExecutionModel.id.asc(),
            )
            .limit(1)
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def create_execution(
        self,
        *,
        configuration_id: UUID,
        user_id: UUID,
        model_version_id: UUID | None,
        execution_parameters: (
            dict[str, Any] | None
        ),
    ) -> SimulationExecutionModel:
        execution = SimulationExecutionModel(
            configuracion_id=configuration_id,
            usuario_id=user_id,
            version_modelo_id=model_version_id,
            estado="PENDIENTE",
            porcentaje_progreso=Decimal("0"),
            parametros_ejecucion=(
                execution_parameters
            ),
            identificador_proceso=None,
        )

        self._session.add(execution)
        await self._session.flush()
        await self._session.refresh(execution)

        return execution

    async def cancel_execution(
        self,
        execution: SimulationExecutionModel,
    ) -> SimulationExecutionModel:
        execution.estado = "CANCELADA"

        await self._session.flush()
        await self._session.refresh(execution)

        return execution

    async def mark_execution_running(
        self,
        execution: SimulationExecutionModel,
    ) -> SimulationExecutionModel:
        execution.estado = "EJECUTANDO"

        await self._session.flush()
        await self._session.refresh(execution)

        return execution

    async def mark_execution_completed(
        self,
        execution: SimulationExecutionModel,
    ) -> SimulationExecutionModel:
        execution.estado = "COMPLETADA"

        await self._session.flush()
        await self._session.refresh(execution)

        return execution

    async def mark_execution_failed(
        self,
        execution: SimulationExecutionModel,
        *,
        error_message: str,
    ) -> SimulationExecutionModel:
        normalized_message = error_message.strip()

        if not normalized_message:
            normalized_message = (
                "La ejecución falló sin mensaje de error"
            )

        execution.estado = "FALLIDA"
        execution.mensaje_error = normalized_message

        await self._session.flush()
        await self._session.refresh(execution)

        return execution

    async def create_result(
        self,
        *,
        execution_id: UUID,
        initial_capital: Decimal,
        total_contributions: Decimal,
        final_capital: Decimal,
        profit_loss: Decimal,
        total_return_percentage: Decimal,
        annualized_return_percentage: Decimal | None,
        annualized_volatility: Decimal | None,
        sharpe_ratio: Decimal | None,
        maximum_drawdown_percentage: Decimal | None,
        value_at_risk: Decimal | None,
        value_at_risk_confidence: Decimal | None,
        best_scenario: Decimal | None,
        worst_scenario: Decimal | None,
        median_scenarios: Decimal | None,
        gain_probability: Decimal | None,
        currency: str,
        summary: dict[str, Any] | None,
    ) -> SimulationResultModel:
        result = SimulationResultModel(
            ejecucion_id=execution_id,
            capital_inicial=initial_capital,
            aportaciones_totales=total_contributions,
            capital_final=final_capital,
            ganancia_perdida=profit_loss,
            rendimiento_total_porcentaje=(
                total_return_percentage
            ),
            rendimiento_anualizado_porcentaje=(
                annualized_return_percentage
            ),
            volatilidad_anualizada=(
                annualized_volatility
            ),
            indice_sharpe=sharpe_ratio,
            maximo_drawdown_porcentaje=(
                maximum_drawdown_percentage
            ),
            valor_en_riesgo=value_at_risk,
            nivel_confianza_var=(
                value_at_risk_confidence
            ),
            mejor_escenario=best_scenario,
            peor_escenario=worst_scenario,
            mediana_escenarios=median_scenarios,
            probabilidad_ganancia=gain_probability,
            moneda=currency,
            resumen=summary,
        )

        self._session.add(result)
        await self._session.flush()
        await self._session.refresh(result)

        return result

    async def create_asset_result(
        self,
        *,
        result_id: UUID,
        asset_id: UUID,
        assigned_percentage: Decimal,
        allocated_capital: Decimal,
        initial_quantity: Decimal | None,
        initial_price: Decimal,
        final_price: Decimal,
        final_value: Decimal,
        profit_loss: Decimal,
        return_percentage: Decimal,
        volatility: Decimal | None,
        maximum_drawdown_percentage: Decimal | None,
        detail: dict[str, Any] | None,
    ) -> SimulationAssetResultModel:
        asset_result = SimulationAssetResultModel(
            resultado_id=result_id,
            activo_id=asset_id,
            porcentaje_asignado=assigned_percentage,
            capital_asignado=allocated_capital,
            cantidad_inicial=initial_quantity,
            precio_inicial=initial_price,
            precio_final=final_price,
            valor_final=final_value,
            ganancia_perdida=profit_loss,
            rendimiento_porcentaje=return_percentage,
            volatilidad=volatility,
            maximo_drawdown_porcentaje=(
                maximum_drawdown_percentage
            ),
            detalle=detail,
        )

        self._session.add(asset_result)
        await self._session.flush()
        await self._session.refresh(
            asset_result
        )

        return asset_result

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()