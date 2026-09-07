import pytest

from alphainvest.modules.simulation.infrastructure.models import (
    SimulationAssetResultModel,
    SimulationConfigurationAssetModel,
    SimulationConfigurationModel,
    SimulationExecutionModel,
    SimulationResultModel,
)

pytestmark = pytest.mark.unit


def test_simulation_table_names() -> None:
    assert (
        SimulationConfigurationModel.__tablename__
        == "configuraciones"
    )
    assert (
        SimulationConfigurationAssetModel.__tablename__
        == "configuracion_activos"
    )
    assert (
        SimulationExecutionModel.__tablename__
        == "ejecuciones"
    )
    assert (
        SimulationResultModel.__tablename__
        == "resultados"
    )
    assert (
        SimulationAssetResultModel.__tablename__
        == "resultados_activo"
    )


def test_simulation_tables_use_correct_schema() -> None:
    models = [
        SimulationConfigurationModel,
        SimulationConfigurationAssetModel,
        SimulationExecutionModel,
        SimulationResultModel,
        SimulationAssetResultModel,
    ]

    for model in models:
        assert model.__table__.schema == "simulation"


def test_configuration_has_composite_asset_relation(
) -> None:
    table = SimulationConfigurationAssetModel.__table__

    assert list(table.primary_key.columns.keys()) == [
        "configuracion_id",
        "activo_id",
    ]


def test_result_has_unique_execution() -> None:
    constraints = {
        constraint.name
        for constraint in (
            SimulationResultModel
            .__table__
            .constraints
        )
    }

    assert "uq_resultados_ejecucion" in constraints


def test_execution_process_identifier_is_unique(
) -> None:
    constraints = {
        constraint.name
        for constraint in (
            SimulationExecutionModel
            .__table__
            .constraints
        )
    }

    assert (
        "uq_ejecuciones_identificador_proceso"
        in constraints
    )


def test_configuration_parameters_store_none_as_sql_null(
) -> None:
    column_type = (
        SimulationConfigurationModel
        .__table__
        .c
        .parametros
        .type
    )

    assert column_type.none_as_null is True


def test_configuration_asset_parameters_use_sql_null(
) -> None:
    column_type = (
        SimulationConfigurationAssetModel
        .__table__
        .c
        .parametros
        .type
    )

    assert column_type.none_as_null is True


def test_execution_parameters_use_sql_null(
) -> None:
    column_type = (
        SimulationExecutionModel
        .__table__
        .c
        .parametros_ejecucion
        .type
    )

    assert column_type.none_as_null is True


