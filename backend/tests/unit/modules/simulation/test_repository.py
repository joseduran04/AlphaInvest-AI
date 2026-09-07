from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.infrastructure.models import (
    SimulationAssetResultModel,
    SimulationConfigurationAssetModel,
    SimulationConfigurationModel,
    SimulationExecutionModel,
    SimulationResultModel,
)
from alphainvest.modules.simulation.infrastructure.repository import (
    SimulationRepository,
)

pytestmark = pytest.mark.unit


def build_session() -> MagicMock:
    session = MagicMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    session.delete = AsyncMock()

    return session


@pytest.mark.asyncio
async def test_get_configuration_by_id_for_user(
) -> None:
    session = build_session()
    configuration = SimpleNamespace(
        id=uuid4(),
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = (
        configuration
    )
    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository
        .get_configuration_by_id_for_user(
            configuration_id=uuid4(),
            user_id=uuid4(),
        )
    )

    assert response is configuration
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_configuration_by_name_for_user(
) -> None:
    session = build_session()
    configuration = SimpleNamespace(
        nombre="Simulación histórica",
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = (
        configuration
    )
    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository
        .get_configuration_by_name_for_user(
            user_id=uuid4(),
            name=" Simulación histórica ",
        )
    )

    assert response is configuration


@pytest.mark.asyncio
async def test_list_configurations_for_user(
) -> None:
    session = build_session()
    configuration = SimpleNamespace(
        id=uuid4(),
    )

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [
        configuration
    ]

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1

    session.execute.side_effect = [
        list_result,
        count_result,
    ]

    repository = SimulationRepository(session)

    items, total = (
        await repository
        .list_configurations_for_user(
            user_id=uuid4(),
            status="BORRADOR",
            limit=50,
            offset=0,
        )
    )

    assert items == [configuration]
    assert total == 1
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_create_configuration() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    user_id = uuid4()

    configuration = (
        await repository.create_configuration(
            user_id=user_id,
            portfolio_id=None,
            name="Simulación histórica",
            description=None,
            simulation_type="HISTORICA",
            initial_capital=Decimal("10000"),
            base_currency="USD",
            start_date=date(2024, 1, 1),
            end_date=date(2025, 1, 1),
            periodic_contribution=Decimal("0"),
            contribution_frequency=None,
            commission_percentage=Decimal("0"),
            annual_inflation=None,
            risk_free_rate=None,
            scenario_count=1,
            random_seed=None,
            parameters=None,
        )
    )

    session.add.assert_called_once_with(
        configuration
    )
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        configuration
    )

    assert isinstance(
        configuration,
        SimulationConfigurationModel,
    )
    assert configuration.usuario_id == user_id
    assert configuration.estado == "BORRADOR"
    assert (
        configuration.tipo_simulacion
        == "HISTORICA"
    )


@pytest.mark.asyncio
async def test_update_configuration_nullable_fields(
) -> None:
    session = build_session()
    repository = SimulationRepository(session)

    configuration = SimpleNamespace(
        portafolio_id=uuid4(),
        nombre="Original",
        descripcion="Descripción",
        tipo_simulacion="HISTORICA",
        capital_inicial=Decimal("10000"),
        moneda_base="USD",
        fecha_inicio=date(2024, 1, 1),
        fecha_fin=date(2025, 1, 1),
        aportacion_periodica=Decimal("0"),
        frecuencia_aportacion=None,
        comision_porcentaje=Decimal("0"),
        inflacion_anual=Decimal("4"),
        tasa_libre_riesgo=Decimal("5"),
        numero_escenarios=1,
        semilla_aleatoria=123,
        parametros={"modo": "prueba"},
    )

    updated = (
        await repository.update_configuration(
            configuration,
            portfolio_id=None,
            portfolio_was_sent=True,
            name="Actualizada",
            description=None,
            description_was_sent=True,
            simulation_type=None,
            initial_capital=None,
            base_currency=None,
            start_date=None,
            end_date=None,
            periodic_contribution=None,
            contribution_frequency=None,
            contribution_frequency_was_sent=True,
            commission_percentage=None,
            annual_inflation=None,
            annual_inflation_was_sent=True,
            risk_free_rate=None,
            risk_free_rate_was_sent=True,
            scenario_count=None,
            random_seed=None,
            random_seed_was_sent=True,
            parameters=None,
            parameters_were_sent=True,
        )
    )

    assert updated is configuration
    assert configuration.portafolio_id is None
    assert configuration.nombre == "Actualizada"
    assert configuration.descripcion is None
    assert (
        configuration.frecuencia_aportacion
        is None
    )
    assert configuration.inflacion_anual is None
    assert configuration.tasa_libre_riesgo is None
    assert configuration.semilla_aleatoria is None
    assert configuration.parametros is None

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        configuration
    )


@pytest.mark.asyncio
async def test_archive_configuration() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    configuration = SimpleNamespace(
        estado="BORRADOR"
    )

    archived = (
        await repository.archive_configuration(
            configuration
        )
    )

    assert archived is configuration
    assert configuration.estado == "ARCHIVADA"
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        configuration
    )


@pytest.mark.asyncio
async def test_commit() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    await repository.commit()

    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_rollback() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    await repository.rollback()

    session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_configuration_asset() -> None:
    session = build_session()
    configuration_asset = SimpleNamespace(
        configuracion_id=uuid4(),
        activo_id=uuid4(),
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = (
        configuration_asset
    )
    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository
        .get_configuration_asset(
            configuration_id=uuid4(),
            asset_id=uuid4(),
        )
    )

    assert response is configuration_asset
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_configuration_assets() -> None:
    session = build_session()
    configuration_asset = SimpleNamespace(
        activo_id=uuid4(),
    )

    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        configuration_asset
    ]
    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository
        .list_configuration_assets(
            configuration_id=uuid4(),
        )
    )

    assert response == [configuration_asset]


@pytest.mark.asyncio
async def test_create_configuration_asset(
) -> None:
    session = build_session()
    repository = SimulationRepository(session)

    configuration_id = uuid4()
    asset_id = uuid4()

    response = (
        await repository
        .create_configuration_asset(
            configuration_id=configuration_id,
            asset_id=asset_id,
            assigned_percentage=Decimal("60"),
            initial_amount=Decimal("6000"),
            initial_price=Decimal("150"),
            order=1,
            parameters={
                "rebalanceo": True,
            },
        )
    )

    assert isinstance(
        response,
        SimulationConfigurationAssetModel,
    )
    assert (
        response.configuracion_id
        == configuration_id
    )
    assert response.activo_id == asset_id
    assert (
        response.porcentaje_asignado
        == Decimal("60")
    )
    assert response.orden == 1

    session.add.assert_called_once_with(response)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        response
    )


@pytest.mark.asyncio
async def test_update_configuration_asset_nullable_fields(
) -> None:
    session = build_session()
    repository = SimulationRepository(session)

    configuration_asset = SimpleNamespace(
        porcentaje_asignado=Decimal("60"),
        monto_inicial=Decimal("6000"),
        precio_inicial=Decimal("150"),
        orden=1,
        parametros={
            "rebalanceo": True,
        },
    )

    response = (
        await repository
        .update_configuration_asset(
            configuration_asset,
            assigned_percentage=Decimal("50"),
            initial_amount=None,
            initial_amount_was_sent=True,
            initial_price=None,
            initial_price_was_sent=True,
            order=2,
            parameters=None,
            parameters_were_sent=True,
        )
    )

    assert response is configuration_asset
    assert (
        configuration_asset.porcentaje_asignado
        == Decimal("50")
    )
    assert configuration_asset.monto_inicial is None
    assert configuration_asset.precio_inicial is None
    assert configuration_asset.orden == 2
    assert configuration_asset.parametros is None

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        configuration_asset
    )


@pytest.mark.asyncio
async def test_delete_configuration_asset(
) -> None:
    session = build_session()
    repository = SimulationRepository(session)

    configuration_asset = SimpleNamespace(
        configuracion_id=uuid4(),
        activo_id=uuid4(),
    )

    await repository.delete_configuration_asset(
        configuration_asset
    )

    session.delete.assert_awaited_once_with(
        configuration_asset
    )
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_distribution_status() -> None:
    session = build_session()
    configuration_id = uuid4()

    row = {
        "configuracion_id": configuration_id,
        "estado": "BORRADOR",
        "capital_inicial": Decimal("10000"),
        "cantidad_activos": 2,
        "porcentaje_total": Decimal("100"),
        "monto_total": Decimal("10000"),
        "distribucion_valida": True,
    }

    mappings = MagicMock()
    mappings.one.return_value = row

    result = MagicMock()
    result.mappings.return_value = mappings
    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository.get_distribution_status(
            configuration_id=configuration_id,
        )
    )

    assert response == row
    assert response["distribucion_valida"] is True


@pytest.mark.asyncio
async def test_mark_configuration_ready() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    configuration = SimpleNamespace(
        estado="BORRADOR"
    )

    response = (
        await repository.mark_configuration_ready(
            configuration
        )
    )

    assert response is configuration
    assert configuration.estado == "LISTA"
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        configuration
    )


@pytest.mark.asyncio
async def test_get_execution_by_id_for_user(
) -> None:
    session = build_session()
    execution = SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = execution
    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository
        .get_execution_by_id_for_user(
            execution_id=execution.id,
            user_id=execution.usuario_id,
        )
    )

    assert response is execution
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_executions_for_user(
) -> None:
    session = build_session()
    execution = SimpleNamespace(
        id=uuid4(),
    )

    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [
        execution
    ]

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1

    session.execute.side_effect = [
        list_result,
        count_result,
    ]

    repository = SimulationRepository(session)

    items, total = (
        await repository.list_executions_for_user(
            user_id=uuid4(),
            status="PENDIENTE",
            configuration_id=uuid4(),
            limit=50,
            offset=0,
        )
    )

    assert items == [execution]
    assert total == 1
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_get_active_execution_for_configuration(
) -> None:
    session = build_session()
    execution = SimpleNamespace(
        id=uuid4(),
        estado="PENDIENTE",
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = execution
    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository
        .get_active_execution_for_configuration(
            configuration_id=uuid4(),
        )
    )

    assert response is execution
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_execution() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    configuration_id = uuid4()
    user_id = uuid4()

    execution = await repository.create_execution(
        configuration_id=configuration_id,
        user_id=user_id,
        model_version_id=None,
        execution_parameters={
            "origen": "TEST",
        },
    )

    assert isinstance(
        execution,
        SimulationExecutionModel,
    )
    assert (
        execution.configuracion_id
        == configuration_id
    )
    assert execution.usuario_id == user_id
    assert execution.version_modelo_id is None
    assert execution.estado == "PENDIENTE"
    assert (
        execution.porcentaje_progreso
        == Decimal("0")
    )
    assert execution.parametros_ejecucion == {
        "origen": "TEST",
    }
    assert execution.identificador_proceso is None

    session.add.assert_called_once_with(execution)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        execution
    )


@pytest.mark.asyncio
async def test_cancel_execution() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    execution = SimpleNamespace(
        estado="PENDIENTE",
    )

    response = await repository.cancel_execution(
        execution
    )

    assert response is execution
    assert execution.estado == "CANCELADA"
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        execution
    )


@pytest.mark.asyncio
async def test_create_result() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    execution_id = uuid4()

    result = await repository.create_result(
        execution_id=execution_id,
        initial_capital=Decimal("10000"),
        total_contributions=Decimal("2000"),
        final_capital=Decimal("13500"),
        profit_loss=Decimal("1500"),
        total_return_percentage=Decimal("12.50"),
        annualized_return_percentage=Decimal("11.20"),
        annualized_volatility=Decimal("18.50"),
        sharpe_ratio=Decimal("0.65"),
        maximum_drawdown_percentage=Decimal("8.25"),
        value_at_risk=Decimal("425"),
        value_at_risk_confidence=Decimal("0.95"),
        best_scenario=None,
        worst_scenario=None,
        median_scenarios=None,
        gain_probability=None,
        currency="USD",
        summary={
            "tipo": "HISTORICA",
        },
    )

    assert isinstance(
        result,
        SimulationResultModel,
    )

    assert result.ejecucion_id == execution_id

    assert (
        result.capital_inicial
        == Decimal("10000")
    )

    assert (
        result.aportaciones_totales
        == Decimal("2000")
    )

    assert (
        result.capital_final
        == Decimal("13500")
    )

    assert (
        result.ganancia_perdida
        == Decimal("1500")
    )

    assert (
        result.rendimiento_total_porcentaje
        == Decimal("12.50")
    )

    assert (
        result.rendimiento_anualizado_porcentaje
        == Decimal("11.20")
    )

    assert (
        result.volatilidad_anualizada
        == Decimal("18.50")
    )

    assert (
        result.indice_sharpe
        == Decimal("0.65")
    )

    assert (
        result.maximo_drawdown_porcentaje
        == Decimal("8.25")
    )

    assert (
        result.valor_en_riesgo
        == Decimal("425")
    )

    assert (
        result.nivel_confianza_var
        == Decimal("0.95")
    )

    assert result.mejor_escenario is None
    assert result.peor_escenario is None
    assert result.mediana_escenarios is None
    assert result.probabilidad_ganancia is None

    assert result.moneda == "USD"

    assert result.resumen == {
        "tipo": "HISTORICA",
    }

    session.add.assert_called_once_with(result)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        result
    )


@pytest.mark.asyncio
async def test_create_asset_result() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    result_id = uuid4()
    asset_id = uuid4()

    asset_result = (
        await repository.create_asset_result(
            result_id=result_id,
            asset_id=asset_id,
            assigned_percentage=Decimal("60"),
            allocated_capital=Decimal("6000"),
            initial_quantity=Decimal("40"),
            initial_price=Decimal("150"),
            final_price=Decimal("165"),
            final_value=Decimal("6600"),
            profit_loss=Decimal("600"),
            return_percentage=Decimal("10"),
            volatility=Decimal("18.25"),
            maximum_drawdown_percentage=(
                Decimal("7.50")
            ),
            detail={
                "aportaciones_totales": "0",
                "cantidad_final": "40",
            },
        )
    )

    assert isinstance(
        asset_result,
        SimulationAssetResultModel,
    )

    assert asset_result.resultado_id == result_id
    assert asset_result.activo_id == asset_id

    assert (
        asset_result.porcentaje_asignado
        == Decimal("60")
    )

    assert (
        asset_result.capital_asignado
        == Decimal("6000")
    )

    assert (
        asset_result.cantidad_inicial
        == Decimal("40")
    )

    assert (
        asset_result.precio_inicial
        == Decimal("150")
    )

    assert (
        asset_result.precio_final
        == Decimal("165")
    )

    assert (
        asset_result.valor_final
        == Decimal("6600")
    )

    assert (
        asset_result.ganancia_perdida
        == Decimal("600")
    )

    assert (
        asset_result.rendimiento_porcentaje
        == Decimal("10")
    )

    assert (
        asset_result.volatilidad
        == Decimal("18.25")
    )

    assert (
        asset_result.maximo_drawdown_porcentaje
        == Decimal("7.50")
    )

    assert asset_result.detalle == {
        "aportaciones_totales": "0",
        "cantidad_final": "40",
    }

    session.add.assert_called_once_with(
        asset_result
    )
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        asset_result
    )


@pytest.mark.asyncio
async def test_mark_execution_running() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    execution = SimpleNamespace(
        estado="PENDIENTE"
    )

    result = await repository.mark_execution_running(
        execution
    )

    assert result is execution
    assert execution.estado == "EJECUTANDO"

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        execution
    )


@pytest.mark.asyncio
async def test_mark_execution_completed() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    execution = SimpleNamespace(
        estado="EJECUTANDO"
    )

    result = (
        await repository.mark_execution_completed(
            execution
        )
    )

    assert result is execution
    assert execution.estado == "COMPLETADA"

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        execution
    )


@pytest.mark.asyncio
async def test_mark_execution_failed() -> None:
    session = build_session()
    repository = SimulationRepository(session)

    execution = SimpleNamespace(
        estado="EJECUTANDO",
        mensaje_error=None,
    )

    result = await repository.mark_execution_failed(
        execution,
        error_message="Error histórico",
    )

    assert result is execution
    assert execution.estado == "FALLIDA"
    assert execution.mensaje_error == (
        "Error histórico"
    )

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        execution
    )


@pytest.mark.asyncio
async def test_get_execution_by_id_for_processing(
) -> None:
    session = build_session()

    execution = SimpleNamespace(
        id=uuid4()
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = (
        execution
    )

    session.execute.return_value = result

    repository = SimulationRepository(session)

    response = (
        await repository
        .get_execution_by_id_for_processing(
            execution_id=execution.id
        )
    )

    assert response is execution
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_pending_executions_for_processing(
) -> None:
    session = build_session()
    repository = SimulationRepository(session)

    first_execution = SimpleNamespace(
        id=uuid4()
    )
    second_execution = SimpleNamespace(
        id=uuid4()
    )

    scalars = MagicMock()
    scalars.all.return_value = [
        first_execution,
        second_execution,
    ]

    result = MagicMock()
    result.scalars.return_value = scalars

    session.execute.return_value = result

    executions = (
        await repository
        .list_pending_executions_for_processing(
            limit=10
        )
    )

    assert executions == [
        first_execution,
        second_execution,
    ]

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_pending_executions_filters_historical(
) -> None:
    session = build_session()
    repository = SimulationRepository(session)

    scalars = MagicMock()
    scalars.all.return_value = []

    result = MagicMock()
    result.scalars.return_value = scalars

    session.execute.return_value = result

    await repository.list_pending_executions_for_processing(
        limit=10
    )

    statement = (
        session.execute.await_args.args[0]
    )

    compiled = str(statement)

    assert "simulation.ejecuciones" in compiled

    assert "simulation.configuraciones" in compiled

    assert (
        "tipo_simulacion" in compiled
    )

    assert (
        "estado" in compiled
    )