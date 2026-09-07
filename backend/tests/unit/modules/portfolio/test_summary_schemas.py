from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.portfolio.presentation.schemas import (
    PortfolioLatestValuationResponse,
    PortfolioOverviewResponse,
    PortfolioSummaryResponse,
)

pytestmark = pytest.mark.unit


def build_summary() -> PortfolioSummaryResponse:
    now = datetime.now(UTC)

    return PortfolioSummaryResponse(
        portafolio_id=uuid4(),
        usuario_id=uuid4(),
        portafolio_nombre="Portafolio principal",
        descripcion=None,
        moneda_base="USD",
        capital_inicial=Decimal("10000"),
        saldo_efectivo=Decimal("2500"),
        tipo="VIRTUAL",
        estado="ACTIVO",
        fecha_inicio=date(2026, 8, 1),
        fecha_cierre=None,
        fecha_creacion=now,
        fecha_actualizacion=now,
        posiciones_abiertas=2,
        posiciones_totales=2,
        capital_invertido=Decimal("7500"),
        valor_posiciones=Decimal("8100"),
        valor_total_estimado=Decimal("10600"),
        ganancia_perdida_posiciones=Decimal(
            "600"
        ),
        ganancia_perdida_total=Decimal("600"),
        rendimiento_estimado_porcentaje=Decimal(
            "6"
        ),
    )


def test_portfolio_summary_accepts_valid_data(
) -> None:
    summary = build_summary()

    assert (
        summary.valor_total_estimado
        == Decimal("10600")
    )
    assert (
        summary.ganancia_perdida_total
        == Decimal("600")
    )
    assert (
        summary.rendimiento_estimado_porcentaje
        == Decimal("6")
    )


def test_summary_allows_null_performance() -> None:
    summary = build_summary()

    updated = summary.model_copy(
        update={
            "capital_inicial": Decimal("0"),
            "rendimiento_estimado_porcentaje": (
                None
            ),
        }
    )

    assert updated.capital_inicial == Decimal("0")
    assert (
        updated.rendimiento_estimado_porcentaje
        is None
    )


def test_overview_allows_missing_valuation() -> None:
    overview = PortfolioOverviewResponse(
        resumen=build_summary(),
        ultima_valoracion=None,
    )

    assert overview.ultima_valoracion is None


def test_overview_accepts_latest_valuation() -> None:
    summary = build_summary()
    now = datetime.now(UTC)

    valuation = PortfolioLatestValuationResponse(
        portafolio_id=summary.portafolio_id,
        fecha_hora=now,
        saldo_efectivo=Decimal("2500"),
        valor_posiciones=Decimal("8100"),
        valor_total=Decimal("10600"),
        capital_invertido=Decimal("7500"),
        ganancia_perdida=Decimal("600"),
        rendimiento_porcentaje=Decimal("6"),
        moneda="USD",
        fecha_registro=now,
    )

    overview = PortfolioOverviewResponse(
        resumen=summary,
        ultima_valoracion=valuation,
    )

    assert overview.ultima_valoracion is not None
    assert (
        overview.ultima_valoracion.valor_total
        == Decimal("10600")
    )