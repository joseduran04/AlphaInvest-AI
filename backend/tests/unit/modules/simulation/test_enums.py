import pytest

from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
    SimulationConfigurationStatus,
    SimulationExecutionStatus,
    SimulationType,
)

pytestmark = pytest.mark.unit


def test_simulation_types_match_database() -> None:
    assert {
        item.value
        for item in SimulationType
    } == {
        "HISTORICA",
        "MONTE_CARLO",
        "PROYECCION",
        "ESCENARIO",
    }


def test_configuration_statuses_match_database(
) -> None:
    assert {
        item.value
        for item in SimulationConfigurationStatus
    } == {
        "BORRADOR",
        "LISTA",
        "ARCHIVADA",
    }


def test_execution_statuses_match_database(
) -> None:
    assert {
        item.value
        for item in SimulationExecutionStatus
    } == {
        "PENDIENTE",
        "EJECUTANDO",
        "COMPLETADA",
        "FALLIDA",
        "CANCELADA",
    }


def test_contribution_frequencies_match_database(
) -> None:
    assert {
        item.value
        for item in ContributionFrequency
    } == {
        "SEMANAL",
        "QUINCENAL",
        "MENSUAL",
        "TRIMESTRAL",
        "SEMESTRAL",
        "ANUAL",
    }