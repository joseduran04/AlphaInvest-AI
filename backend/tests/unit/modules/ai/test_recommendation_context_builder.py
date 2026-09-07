from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.recommendation_context_builder import (
    RecommendationContextBuilder,
)

pytestmark = pytest.mark.unit


def build_recommendation_request() -> SimpleNamespace:
    asset_id = uuid4()
    prediction_request_id = uuid4()

    return SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        portafolio_id=uuid4(),
        perfil_riesgo_id=None,
        tipo_analisis="RECOMENDACION",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(2026, 8, 27),
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
        },
        estado="PENDIENTE",
    )


def build_prediction(
    *,
    asset_id,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        solicitud_id=uuid4(),
        activo_id=asset_id,
        version_modelo_id=uuid4(),
        fecha_base=date(2026, 8, 26),
        fecha_objetivo=date(2026, 8, 27),
        horizonte="CORTO_PLAZO",
        precio_base=Decimal("100"),
        precio_predicho=Decimal("105"),
        rendimiento_esperado_porcentaje=(
            Decimal("5")
        ),
        tendencia="ALCISTA",
        confianza=Decimal("0.80"),
        probabilidad_alcista=Decimal("0.80"),
        probabilidad_neutral=Decimal("0.10"),
        probabilidad_bajista=Decimal("0.10"),
    )


@pytest.mark.asyncio
async def test_builds_complete_recommendation_context() -> None:
    request = build_recommendation_request()

    parameters = request.parametros

    assert isinstance(parameters, dict)

    asset_id = uuid4()

    parameters["asset_id"] = str(asset_id)

    prediction_request_id = uuid4()

    parameters[
        "prediction_request_id"
    ] = str(prediction_request_id)

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=request.usuario_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    prediction = build_prediction(
        asset_id=asset_id
    )

    latest_price = SimpleNamespace(
        cierre=Decimal("101"),
        fecha=date(2026, 8, 27),
    )

    indicators = [
        SimpleNamespace(
            tipo_indicador="EMA",
            periodo="20D",
            valor=Decimal("99"),
            fecha=date(2026, 8, 27),
        ),
        SimpleNamespace(
            tipo_indicador="RSI",
            periodo="14D",
            valor=Decimal("55"),
            fecha=date(2026, 8, 27),
        ),
    ]

    profile = SimpleNamespace(
        id=uuid4(),
        usuario_id=request.usuario_id,
        clasificacion="MODERADO",
        puntuacion=Decimal("50"),
        confianza=Decimal("0.90"),
        vigente=True,
    )

    portfolio = SimpleNamespace(
        id=request.portafolio_id,
        usuario_id=request.usuario_id,
        capital_inicial=Decimal("10000"),
        saldo_efectivo=Decimal("5000"),
        estado="ACTIVO",
    )

    position = SimpleNamespace(
        id=uuid4(),
        portafolio_id=portfolio.id,
        activo_id=asset_id,
        cantidad=Decimal("10"),
        precio_promedio_compra=(
            Decimal("95")
        ),
        costo_total=Decimal("950"),
        precio_actual=Decimal("101"),
        valor_actual=Decimal("1010"),
        ganancia_perdida=Decimal("60"),
        rendimiento_porcentaje=(
            Decimal("6.31578947")
        ),
        estado="ABIERTA",
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=prediction_request
        ),
        get_asset_prediction_by_request=(
            AsyncMock(
                return_value=prediction
            )
        ),
    )

    market_repository = SimpleNamespace(
        get_latest_asset_price=AsyncMock(
            return_value=latest_price
        ),
        list_financial_indicators_for_ai=(
            AsyncMock(
                return_value=indicators
            )
        ),
    )

    profile_repository = SimpleNamespace(
        get_current_profile=AsyncMock(
            return_value=profile
        ),
    )

    portfolio_repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(
            return_value=portfolio
        ),
        get_position_by_asset=AsyncMock(
            return_value=position
        ),
    )

    builder = RecommendationContextBuilder(
        ai_repository=ai_repository,
        market_repository=market_repository,
        profile_repository=profile_repository,
        portfolio_repository=portfolio_repository,
    )

    context = await builder.build(
        request=request
    )

    assert context.request_id == request.id
    assert context.user_id == request.usuario_id
    assert context.asset_id == asset_id

    assert (
        context.prediction.prediction_id
        == prediction.id
    )

    assert (
        context.prediction.trend
        == "ALCISTA"
    )

    assert (
        context.prediction.confidence
        == Decimal("0.80")
    )

    assert (
        context.latest_price
        == Decimal("101")
    )

    assert len(context.indicators) == 2

    assert (
        context.indicators[0].indicator_type
        == "EMA"
    )

    assert context.risk_profile is not None

    assert (
        context.risk_profile.classification
        == "MODERADO"
    )

    assert context.portfolio is not None
    assert context.portfolio.position is not None

    assert (
        context.portfolio.position.quantity
        == Decimal("10")
    )

    ai_repository.get_analysis_request.assert_awaited_once_with(
        prediction_request_id
    )

    (
        ai_repository
        .get_asset_prediction_by_request
        .assert_awaited_once_with(
            request_id=prediction_request_id
        )
    )

    market_repository.get_latest_asset_price.assert_awaited_once_with(
        asset_id=asset_id
    )

    profile_repository.get_current_profile.assert_awaited_once_with(
        request.usuario_id
    )

    portfolio_repository.get_by_id_for_user.assert_awaited_once_with(
        portfolio_id=request.portafolio_id,
        user_id=request.usuario_id,
    )

    portfolio_repository.get_position_by_asset.assert_awaited_once_with(
        portfolio_id=request.portafolio_id,
        asset_id=asset_id,
    )


@pytest.mark.asyncio
async def test_builds_context_without_optional_portfolio() -> None:
    request = build_recommendation_request()
    request.portafolio_id = None

    parameters = request.parametros

    assert isinstance(parameters, dict)

    asset_id = uuid4()
    prediction_request_id = uuid4()

    parameters["asset_id"] = str(asset_id)
    parameters[
        "prediction_request_id"
    ] = str(prediction_request_id)

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=request.usuario_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=prediction_request
        ),
        get_asset_prediction_by_request=(
            AsyncMock(
                return_value=build_prediction(
                    asset_id=asset_id
                )
            )
        ),
    )

    market_repository = SimpleNamespace(
        get_latest_asset_price=AsyncMock(
            return_value=None
        ),
        list_financial_indicators_for_ai=(
            AsyncMock(
                return_value=[]
            )
        ),
    )

    profile_repository = SimpleNamespace(
        get_current_profile=AsyncMock(
            return_value=None
        ),
    )

    portfolio_repository = SimpleNamespace(
        get_by_id_for_user=AsyncMock(),
        get_position_by_asset=AsyncMock(),
    )

    builder = RecommendationContextBuilder(
        ai_repository=ai_repository,
        market_repository=market_repository,
        profile_repository=profile_repository,
        portfolio_repository=portfolio_repository,
    )

    context = await builder.build(
        request=request
    )

    assert context.portfolio is None
    assert context.risk_profile is None
    assert context.latest_price is None
    assert context.indicators == ()

    (
        portfolio_repository
        .get_by_id_for_user
        .assert_not_awaited()
    )

    (
        portfolio_repository
        .get_position_by_asset
        .assert_not_awaited()
    )


@pytest.mark.asyncio
async def test_rejects_wrong_request_type() -> None:
    request = build_recommendation_request()
    request.tipo_analisis = "ACTIVO"

    builder = RecommendationContextBuilder(
        ai_repository=SimpleNamespace(),
        market_repository=SimpleNamespace(),
        profile_repository=SimpleNamespace(),
        portfolio_repository=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="RECOMENDACION",
    ):
        await builder.build(
            request=request
        )


@pytest.mark.asyncio
async def test_rejects_completed_recommendation_request() -> None:
    request = build_recommendation_request()
    request.estado = "COMPLETADA"

    builder = RecommendationContextBuilder(
        ai_repository=SimpleNamespace(),
        market_repository=SimpleNamespace(),
        profile_repository=SimpleNamespace(),
        portfolio_repository=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="estado procesable",
    ):
        await builder.build(
            request=request
        )


@pytest.mark.asyncio
async def test_rejects_invalid_asset_id() -> None:
    request = build_recommendation_request()

    parameters = request.parametros

    assert isinstance(parameters, dict)

    parameters["asset_id"] = "invalid-uuid"

    builder = RecommendationContextBuilder(
        ai_repository=SimpleNamespace(),
        market_repository=SimpleNamespace(),
        profile_repository=SimpleNamespace(),
        portfolio_repository=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="asset_id",
    ):
        await builder.build(
            request=request
        )


@pytest.mark.asyncio
async def test_rejects_missing_prediction_request() -> None:
    request = build_recommendation_request()

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=None
        )
    )

    builder = RecommendationContextBuilder(
        ai_repository=ai_repository,
        market_repository=SimpleNamespace(),
        profile_repository=SimpleNamespace(),
        portfolio_repository=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="solicitud ACTIVO asociada",
    ):
        await builder.build(
            request=request
        )


@pytest.mark.asyncio
async def test_rejects_prediction_request_from_other_user() -> None:
    request = build_recommendation_request()

    parameters = request.parametros

    assert isinstance(parameters, dict)

    prediction_request = SimpleNamespace(
        id=uuid4(),
        usuario_id=uuid4(),
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=prediction_request
        )
    )

    builder = RecommendationContextBuilder(
        ai_repository=ai_repository,
        market_repository=SimpleNamespace(),
        profile_repository=SimpleNamespace(),
        portfolio_repository=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="mismo usuario",
    ):
        await builder.build(
            request=request
        )


@pytest.mark.asyncio
async def test_rejects_incomplete_prediction_request() -> None:
    request = build_recommendation_request()

    prediction_request = SimpleNamespace(
        id=uuid4(),
        usuario_id=request.usuario_id,
        tipo_analisis="ACTIVO",
        estado="PENDIENTE",
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=prediction_request
        )
    )

    builder = RecommendationContextBuilder(
        ai_repository=ai_repository,
        market_repository=SimpleNamespace(),
        profile_repository=SimpleNamespace(),
        portfolio_repository=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="COMPLETADA",
    ):
        await builder.build(
            request=request
        )


@pytest.mark.asyncio
async def test_rejects_prediction_for_another_asset() -> None:
    request = build_recommendation_request()

    parameters = request.parametros

    assert isinstance(parameters, dict)

    prediction_request_id = uuid4()

    parameters[
        "prediction_request_id"
    ] = str(prediction_request_id)

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=request.usuario_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    prediction = build_prediction(
        asset_id=uuid4()
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=prediction_request
        ),
        get_asset_prediction_by_request=(
            AsyncMock(
                return_value=prediction
            )
        ),
    )

    builder = RecommendationContextBuilder(
        ai_repository=ai_repository,
        market_repository=SimpleNamespace(),
        profile_repository=SimpleNamespace(),
        portfolio_repository=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="no pertenece al activo",
    ):
        await builder.build(
            request=request
        )