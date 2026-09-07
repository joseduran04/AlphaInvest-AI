import pytest

from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisHorizon,
    AnalysisRequestStatus,
    AnalysisType,
)

pytestmark = pytest.mark.unit


def test_analysis_types_match_database_values() -> None:
    assert AnalysisType.ASSET.value == "ACTIVO"

    assert (
        AnalysisType.PORTFOLIO.value
        == "PORTAFOLIO"
    )

    assert AnalysisType.MARKET.value == "MERCADO"

    assert (
        AnalysisType.SENTIMENT.value
        == "SENTIMIENTO"
    )

    assert (
        AnalysisType.RECOMMENDATION.value
        == "RECOMENDACION"
    )

    assert (
        AnalysisType.SIMULATION.value
        == "SIMULACION"
    )

    assert AnalysisType.INTEGRAL.value == "INTEGRAL"


def test_analysis_horizons_match_database() -> None:
    assert (
        AnalysisHorizon.INTRADAY.value
        == "INTRADIA"
    )

    assert (
        AnalysisHorizon.SHORT_TERM.value
        == "CORTO_PLAZO"
    )

    assert (
        AnalysisHorizon.MEDIUM_TERM.value
        == "MEDIANO_PLAZO"
    )

    assert (
        AnalysisHorizon.LONG_TERM.value
        == "LARGO_PLAZO"
    )


def test_analysis_statuses_match_database() -> None:
    assert (
        AnalysisRequestStatus.PENDING.value
        == "PENDIENTE"
    )

    assert (
        AnalysisRequestStatus.RUNNING.value
        == "EJECUTANDO"
    )

    assert (
        AnalysisRequestStatus.COMPLETED.value
        == "COMPLETADA"
    )

    assert (
        AnalysisRequestStatus.FAILED.value
        == "FALLIDA"
    )

    assert (
        AnalysisRequestStatus.CANCELLED.value
        == "CANCELADA"
    )