from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.analysis_request_service import (
    AnalysisRequestService,
)
from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisHorizon,
    AnalysisRequestStatus,
    AnalysisType,
)
from alphainvest.modules.ai.domain.exceptions import (
    AnalysisRequestInvalidParametersError,
    AnalysisRequestInvalidStateError,
    AnalysisRequestNotFoundError,
    AnalysisResultNotFoundError,
    AnalysisResultNotReadyError,
)
from alphainvest.modules.ai.presentation.schemas import (
    AssetAnalysisRequestCreate,
    IntegralAnalysisRequestCreate,
    RecommendationRequestCreate,
    SentimentAnalysisRequestCreate,
)

pytestmark = pytest.mark.unit


def build_analysis_request(
    *,
    user_id: object,
    asset_id: object,
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        portafolio_id=None,
        perfil_riesgo_id=None,
        ejecucion_simulacion_id=None,
        tipo_analisis="ACTIVO",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(2026, 8, 14),
        parametros={
            "asset_id": str(asset_id),
        },
        estado="PENDIENTE",
        porcentaje_progreso=Decimal("0"),
        fecha_solicitud=now,
        fecha_inicio=None,
        fecha_fin=None,
        mensaje_error=None,
        identificador_proceso=None,
        fecha_expiracion=None,
    )


@pytest.mark.asyncio
async def test_creates_asset_analysis_request() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    stored = build_analysis_request(
        user_id=user_id,
        asset_id=asset_id,
    )

    repository = SimpleNamespace(
        create_analysis_request=AsyncMock(
            return_value=stored
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = AnalysisRequestService(
        repository
    )

    request = AssetAnalysisRequestCreate(
        asset_id=asset_id,
        horizon=AnalysisHorizon.SHORT_TERM,
        reference_date=date(2026, 8, 14),
    )

    response = await service.create_asset_request(
        user_id=user_id,
        request=request,
    )

    assert response.user_id == user_id

    assert (
        response.analysis_type.value
        == "ACTIVO"
    )

    assert (
        response.horizon
        == AnalysisHorizon.SHORT_TERM
    )

    assert (
        response.status
        == AnalysisRequestStatus.PENDING
    )

    assert response.parameters == {
        "asset_id": str(asset_id),
    }

    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_gets_own_analysis_request() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    stored = build_analysis_request(
        user_id=user_id,
        asset_id=asset_id,
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=stored
        )
    )

    service = AnalysisRequestService(
        repository
    )

    response = await service.get_user_request(
        request_id=stored.id,
        user_id=user_id,
    )

    assert response.id == stored.id
    assert response.user_id == user_id


@pytest.mark.asyncio
async def test_rejects_missing_or_foreign_request() -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=None
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestNotFoundError
    ):
        await service.get_user_request(
            request_id=uuid4(),
            user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_get_user_result() -> None:
    request_id = uuid4()
    user_id = uuid4()

    trend_version_id = uuid4()
    price_version_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        usuario_id=user_id,
        estado="COMPLETADA",
        horizonte="CORTO_PLAZO",
    )

    prediction = SimpleNamespace(
        solicitud_id=request_id,
        activo_id=uuid4(),
        version_modelo_id=(
            trend_version_id
        ),
        fecha_base=date(2026, 8, 14),
        fecha_objetivo=date(2026, 8, 21),
        precio_base=Decimal(
            "305.92999268"
        ),
        precio_predicho=Decimal(
            "308.21387360"
        ),
        rendimiento_esperado_porcentaje=(
            Decimal("0.74653711")
        ),
        tendencia="BAJISTA",
        confianza=Decimal("0.6389"),
        probabilidad_alcista=Decimal(
            "0.1069"
        ),
        probabilidad_neutral=Decimal(
            "0.2541"
        ),
        probabilidad_bajista=Decimal(
            "0.6389"
        ),
        salida_modelo={
            "price_forecast_version_id": str(
                price_version_id
            )
        },
        fecha_generacion=datetime(
            2026,
            8,
            23,
            tzinfo=UTC,
        ),
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=request
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=prediction
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    result = await service.get_user_result(
        request_id=request_id,
        user_id=user_id,
    )

    assert result.request_id == request_id

    assert result.trend == "BAJISTA"

    assert (
        result.target_date
        == date(2026, 8, 21)
    )

    assert (
        result.predicted_price
        == Decimal("308.21387360")
    )

    assert (
        result.price_forecast_version_id
        == price_version_id
    )

    assert (
        result.probabilities.bearish
        == Decimal("0.6389")
    )


@pytest.mark.asyncio
async def test_rejects_result_when_request_not_completed() -> None:
    request = SimpleNamespace(
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=request
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotReadyError
    ):
        await service.get_user_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_creates_sentiment_request() -> None:
    user_id = uuid4()
    asset_id = uuid4()
    news_reference_id = uuid4()

    stored = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        portafolio_id=None,
        perfil_riesgo_id=None,
        ejecucion_simulacion_id=None,
        tipo_analisis="SENTIMIENTO",
        horizonte=None,
        fecha_referencia=date(
            2026,
            8,
            26,
        ),
        parametros={
            "asset_id": str(
                asset_id
            ),
            "news_reference_id": str(
                news_reference_id
            ),
        },
        estado="PENDIENTE",
        porcentaje_progreso=Decimal("0"),
        fecha_solicitud=datetime.now(
            UTC
        ),
        fecha_inicio=None,
        fecha_fin=None,
        mensaje_error=None,
        identificador_proceso=None,
        fecha_expiracion=None,
    )

    repository = SimpleNamespace(
        create_analysis_request=AsyncMock(
            return_value=stored
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = AnalysisRequestService(
        repository
    )

    request = SentimentAnalysisRequestCreate(
        asset_id=asset_id,
        news_reference_id=(
            news_reference_id
        ),
        reference_date=date(
            2026,
            8,
            26,
        ),
    )

    response = (
        await service
        .create_sentiment_request(
            user_id=user_id,
            request=request,
        )
    )

    assert (
        response.analysis_type
        == AnalysisType.SENTIMENT
    )

    assert response.horizon is None

    call = (
        repository
        .create_analysis_request
        .await_args
    )

    assert call is not None

    kwargs = call.kwargs

    assert (
        kwargs["analysis_type"]
        == "SENTIMIENTO"
    )

    assert kwargs["horizon"] is None

    assert (
        kwargs["parameters"]
        == {
            "asset_id": str(
                asset_id
            ),
            "news_reference_id": str(
                news_reference_id
            ),
        }
    )

    repository.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_creates_recommendation_request() -> None:
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    portfolio_id = uuid4()

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=user_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    prediction = SimpleNamespace(
        activo_id=asset_id
    )

    stored = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        portafolio_id=portfolio_id,
        perfil_riesgo_id=None,
        ejecucion_simulacion_id=None,
        tipo_analisis="RECOMENDACION",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            27,
        ),
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
        },
        estado="PENDIENTE",
        porcentaje_progreso=Decimal("0"),
        fecha_solicitud=datetime.now(
            UTC
        ),
        fecha_inicio=None,
        fecha_fin=None,
        mensaje_error=None,
        identificador_proceso=None,
        fecha_expiracion=None,
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=prediction_request
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=prediction
        ),
        create_analysis_request=AsyncMock(
            return_value=stored
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = AnalysisRequestService(
        repository
    )

    request = RecommendationRequestCreate(
        asset_id=asset_id,
        prediction_request_id=(
            prediction_request_id
        ),
        portfolio_id=portfolio_id,
        horizon=AnalysisHorizon.SHORT_TERM,
        reference_date=date(
            2026,
            8,
            27,
        ),
    )

    response = (
        await service
        .create_recommendation_request(
            user_id=user_id,
            request=request,
        )
    )

    assert (
        response.analysis_type
        == AnalysisType.RECOMMENDATION
    )
    assert (
        response.status
        == AnalysisRequestStatus.PENDING
    )
    assert response.portfolio_id == portfolio_id

    assert response.parameters == {
        "asset_id": str(asset_id),
        "prediction_request_id": str(
            prediction_request_id
        ),
    }

    (
        repository
        .get_analysis_request_for_user
        .assert_awaited_once_with(
            request_id=prediction_request_id,
            user_id=user_id,
        )
    )

    (
        repository
        .get_asset_prediction_by_request
        .assert_awaited_once_with(
            request_id=prediction_request_id
        )
    )

    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()

@pytest.mark.asyncio
async def test_rejects_recommendation_with_missing_prediction_request() -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=None
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestNotFoundError
    ):
        await service.create_recommendation_request(
            user_id=uuid4(),
            request=RecommendationRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    27,
                ),
            ),
        )

@pytest.mark.asyncio
async def test_rejects_recommendation_with_non_asset_request() -> None:
    user_id = uuid4()

    source_request = SimpleNamespace(
        tipo_analisis="SENTIMIENTO",
        estado="COMPLETADA",
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=source_request
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await service.create_recommendation_request(
            user_id=user_id,
            request=RecommendationRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    27,
                ),
            ),
        )

@pytest.mark.asyncio
async def test_rejects_recommendation_when_asset_request_not_completed() -> None:
    user_id = uuid4()

    source_request = SimpleNamespace(
        tipo_analisis="ACTIVO",
        estado="PENDIENTE",
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=source_request
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidStateError
    ):
        await service.create_recommendation_request(
            user_id=user_id,
            request=RecommendationRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    27,
                ),
            ),
        )

@pytest.mark.asyncio
async def test_rejects_recommendation_for_different_asset() -> None:
    user_id = uuid4()

    source_request = SimpleNamespace(
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=source_request
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=uuid4()
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await service.create_recommendation_request(
            user_id=user_id,
            request=RecommendationRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    27,
                ),
            ),
        )

@pytest.mark.asyncio
async def test_creates_integral_request_without_sentiment() -> None:
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    portfolio_id = uuid4()

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=user_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    prediction = SimpleNamespace(
        activo_id=asset_id
    )

    stored = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        portafolio_id=portfolio_id,
        perfil_riesgo_id=None,
        ejecucion_simulacion_id=None,
        tipo_analisis="INTEGRAL",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            29,
        ),
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
            "sentiment_request_ids": [],
        },
        estado="PENDIENTE",
        porcentaje_progreso=Decimal("0"),
        fecha_solicitud=datetime.now(
            UTC
        ),
        fecha_inicio=None,
        fecha_fin=None,
        mensaje_error=None,
        identificador_proceso=None,
        fecha_expiracion=None,
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=prediction_request
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=prediction
        ),
        get_sentiment_analysis_by_request=AsyncMock(),
        create_analysis_request=AsyncMock(
            return_value=stored
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = AnalysisRequestService(
        repository
    )

    request = IntegralAnalysisRequestCreate(
        asset_id=asset_id,
        prediction_request_id=(
            prediction_request_id
        ),
        sentiment_request_ids=[],
        portfolio_id=portfolio_id,
        horizon=AnalysisHorizon.SHORT_TERM,
        reference_date=date(
            2026,
            8,
            29,
        ),
    )

    response = (
        await service
        .create_integral_request(
            user_id=user_id,
            request=request,
        )
    )

    assert (
        response.analysis_type
        == AnalysisType.INTEGRAL
    )

    assert (
        response.status
        == AnalysisRequestStatus.PENDING
    )

    assert response.portfolio_id == portfolio_id

    assert response.parameters == {
        "asset_id": str(asset_id),
        "prediction_request_id": str(
            prediction_request_id
        ),
        "sentiment_request_ids": [],
    }

    (
        repository
        .get_analysis_request_for_user
        .assert_awaited_once_with(
            request_id=prediction_request_id,
            user_id=user_id,
        )
    )

    (
        repository
        .get_asset_prediction_by_request
        .assert_awaited_once_with(
            request_id=prediction_request_id
        )
    )

    (
        repository
        .get_sentiment_analysis_by_request
        .assert_not_awaited()
    )

    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_creates_integral_request_with_sentiment() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    prediction_request_id = uuid4()
    sentiment_request_id = uuid4()

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=user_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    sentiment_request = SimpleNamespace(
        id=sentiment_request_id,
        usuario_id=user_id,
        tipo_analisis="SENTIMIENTO",
        estado="COMPLETADA",
    )

    prediction = SimpleNamespace(
        activo_id=asset_id
    )

    sentiment_analysis = SimpleNamespace(
        activo_id=asset_id
    )

    stored = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        portafolio_id=None,
        perfil_riesgo_id=None,
        ejecucion_simulacion_id=None,
        tipo_analisis="INTEGRAL",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            29,
        ),
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
            "sentiment_request_ids": [
                str(sentiment_request_id)
            ],
        },
        estado="PENDIENTE",
        porcentaje_progreso=Decimal("0"),
        fecha_solicitud=datetime.now(
            UTC
        ),
        fecha_inicio=None,
        fecha_fin=None,
        mensaje_error=None,
        identificador_proceso=None,
        fecha_expiracion=None,
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            side_effect=[
                prediction_request,
                sentiment_request,
            ]
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=prediction
        ),
        get_sentiment_analysis_by_request=AsyncMock(
            return_value=sentiment_analysis
        ),
        create_analysis_request=AsyncMock(
            return_value=stored
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = AnalysisRequestService(
        repository
    )

    response = await service.create_integral_request(
        user_id=user_id,
        request=IntegralAnalysisRequestCreate(
            asset_id=asset_id,
            prediction_request_id=(
                prediction_request_id
            ),
            sentiment_request_ids=[
                sentiment_request_id
            ],
            reference_date=date(
                2026,
                8,
                29,
            ),
        ),
    )

    assert (
        response.analysis_type
        == AnalysisType.INTEGRAL
    )

    assert response.parameters == {
        "asset_id": str(asset_id),
        "prediction_request_id": str(
            prediction_request_id
        ),
        "sentiment_request_ids": [
            str(sentiment_request_id)
        ],
    }

    (
        repository
        .get_sentiment_analysis_by_request
        .assert_awaited_once_with(
            request_id=sentiment_request_id
        )
    )

    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_integral_with_duplicate_sentiment_requests() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    prediction_request_id = uuid4()
    sentiment_request_id = uuid4()

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="ACTIVO",
                estado="COMPLETADA",
            )
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=asset_id
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await service.create_integral_request(
            user_id=user_id,
            request=IntegralAnalysisRequestCreate(
                asset_id=asset_id,
                prediction_request_id=(
                    prediction_request_id
                ),
                sentiment_request_ids=[
                    sentiment_request_id,
                    sentiment_request_id,
                ],
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_with_missing_prediction_request() -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=None
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestNotFoundError
    ):
        await service.create_integral_request(
            user_id=uuid4(),
            request=IntegralAnalysisRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_with_non_asset_prediction_request() -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="SENTIMIENTO",
                estado="COMPLETADA",
            )
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await service.create_integral_request(
            user_id=uuid4(),
            request=IntegralAnalysisRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_when_asset_request_not_completed() -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="ACTIVO",
                estado="PENDIENTE",
            )
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidStateError
    ):
        await service.create_integral_request(
            user_id=uuid4(),
            request=IntegralAnalysisRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_for_different_prediction_asset() -> None:
    user_id = uuid4()

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="ACTIVO",
                estado="COMPLETADA",
            )
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=uuid4()
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await service.create_integral_request(
            user_id=user_id,
            request=IntegralAnalysisRequestCreate(
                asset_id=uuid4(),
                prediction_request_id=uuid4(),
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_with_missing_sentiment_request() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    prediction_request = SimpleNamespace(
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            side_effect=[
                prediction_request,
                None,
            ]
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=asset_id
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestNotFoundError
    ):
        await service.create_integral_request(
            user_id=user_id,
            request=IntegralAnalysisRequestCreate(
                asset_id=asset_id,
                prediction_request_id=uuid4(),
                sentiment_request_ids=[
                    uuid4()
                ],
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_with_non_sentiment_request() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            side_effect=[
                SimpleNamespace(
                    tipo_analisis="ACTIVO",
                    estado="COMPLETADA",
                ),
                SimpleNamespace(
                    tipo_analisis="ACTIVO",
                    estado="COMPLETADA",
                ),
            ]
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=asset_id
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await service.create_integral_request(
            user_id=user_id,
            request=IntegralAnalysisRequestCreate(
                asset_id=asset_id,
                prediction_request_id=uuid4(),
                sentiment_request_ids=[
                    uuid4()
                ],
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_when_sentiment_not_completed() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            side_effect=[
                SimpleNamespace(
                    tipo_analisis="ACTIVO",
                    estado="COMPLETADA",
                ),
                SimpleNamespace(
                    tipo_analisis="SENTIMIENTO",
                    estado="PENDIENTE",
                ),
            ]
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=asset_id
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidStateError
    ):
        await service.create_integral_request(
            user_id=user_id,
            request=IntegralAnalysisRequestCreate(
                asset_id=asset_id,
                prediction_request_id=uuid4(),
                sentiment_request_ids=[
                    uuid4()
                ],
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_without_persisted_sentiment_analysis() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            side_effect=[
                SimpleNamespace(
                    tipo_analisis="ACTIVO",
                    estado="COMPLETADA",
                ),
                SimpleNamespace(
                    tipo_analisis="SENTIMIENTO",
                    estado="COMPLETADA",
                ),
            ]
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=asset_id
            )
        ),
        get_sentiment_analysis_by_request=AsyncMock(
            return_value=None
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotFoundError
    ):
        await service.create_integral_request(
            user_id=user_id,
            request=IntegralAnalysisRequestCreate(
                asset_id=asset_id,
                prediction_request_id=uuid4(),
                sentiment_request_ids=[
                    uuid4()
                ],
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )


@pytest.mark.asyncio
async def test_rejects_integral_with_sentiment_from_different_asset() -> None:
    user_id = uuid4()
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            side_effect=[
                SimpleNamespace(
                    tipo_analisis="ACTIVO",
                    estado="COMPLETADA",
                ),
                SimpleNamespace(
                    tipo_analisis="SENTIMIENTO",
                    estado="COMPLETADA",
                ),
            ]
        ),
        get_asset_prediction_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=asset_id
            )
        ),
        get_sentiment_analysis_by_request=AsyncMock(
            return_value=SimpleNamespace(
                activo_id=uuid4()
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await service.create_integral_request(
            user_id=user_id,
            request=IntegralAnalysisRequestCreate(
                asset_id=asset_id,
                prediction_request_id=uuid4(),
                sentiment_request_ids=[
                    uuid4()
                ],
                reference_date=date(
                    2026,
                    8,
                    29,
                ),
            ),
        )

@pytest.mark.asyncio
async def test_gets_integral_result_from_recommendation(
) -> None:
    integral_request_id = uuid4()
    recommendation_request_id = uuid4()
    user_id = uuid4()

    integral_request = SimpleNamespace(
        id=integral_request_id,
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="COMPLETADA",
        parametros={
            "recommendation_request_id": str(
                recommendation_request_id
            ),
        },
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=integral_request
        )
    )

    service = AnalysisRequestService(
        repository
    )

    expected_result = SimpleNamespace(
        request_id=recommendation_request_id
    )

    service.get_user_recommendation_result = (
        AsyncMock(
            return_value=expected_result
        )
    )

    result = await service.get_user_integral_result(
        request_id=integral_request_id,
        user_id=user_id,
    )

    assert result is expected_result

    (
        repository
        .get_analysis_request_for_user
        .assert_awaited_once_with(
            request_id=integral_request_id,
            user_id=user_id,
        )
    )

    (
        service
        .get_user_recommendation_result
        .assert_awaited_once_with(
            request_id=recommendation_request_id,
            user_id=user_id,
        )
    )

@pytest.mark.asyncio
async def test_rejects_missing_integral_result_request(
) -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=None
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestNotFoundError
    ):
        await service.get_user_integral_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )

@pytest.mark.asyncio
async def test_rejects_non_integral_result_request(
) -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="RECOMENDACION",
                estado="COMPLETADA",
            )
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisRequestNotFoundError
    ):
        await service.get_user_integral_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )

@pytest.mark.asyncio
async def test_rejects_unfinished_integral_result(
) -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="INTEGRAL",
                estado="PENDIENTE",
            )
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotReadyError
    ):
        await service.get_user_integral_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )

@pytest.mark.asyncio
async def test_rejects_integral_result_without_parameters(
) -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="INTEGRAL",
                estado="COMPLETADA",
                parametros=None,
            )
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotFoundError
    ):
        await service.get_user_integral_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )

@pytest.mark.asyncio
async def test_rejects_integral_result_without_recommendation_request(
) -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="INTEGRAL",
                estado="COMPLETADA",
                parametros={
                    "asset_id": str(
                        uuid4()
                    ),
                },
            )
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotFoundError
    ):
        await service.get_user_integral_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )

@pytest.mark.asyncio
async def test_rejects_integral_result_with_invalid_recommendation_id(
) -> None:
    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=SimpleNamespace(
                tipo_analisis="INTEGRAL",
                estado="COMPLETADA",
                parametros={
                    "recommendation_request_id": (
                        "invalid-uuid"
                    ),
                },
            )
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotFoundError
    ):
        await service.get_user_integral_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )



@pytest.mark.asyncio
async def test_gets_recommendation_result() -> None:
    request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    recommendation_id = uuid4()
    version_id = uuid4()

    analysis_request = SimpleNamespace(
        id=request_id,
        usuario_id=user_id,
        tipo_analisis="RECOMENDACION",
        estado="COMPLETADA",
        parametros={
            "asset_id": str(asset_id),
        },
    )

    recommendation = SimpleNamespace(
        id=recommendation_id,
        usuario_id=user_id,
        perfil_riesgo_id=None,
        portafolio_id=None,
        version_modelo_id=version_id,
        tipo="OBSERVAR",
        titulo="Observar activo",
        resumen="Se recomienda observar.",
        justificacion="Señales mixtas.",
        nivel_riesgo="MEDIO",
        horizonte="CORTO_PLAZO",
        confianza=Decimal("0.60"),
        prioridad=1,
        estado="GENERADA",
        advertencia=(
            "Contenido educativo."
        ),
        parametros={
            "engine": "deterministic_v1"
        },
        fecha_generacion=datetime(
            2026,
            8,
            27,
            tzinfo=UTC,
        ),
        fecha_expiracion=None,
    )

    recommendation_asset = SimpleNamespace(
        activo_id=asset_id,
        accion="OBSERVAR",
        porcentaje_objetivo=None,
        precio_referencia=Decimal("100"),
        precio_objetivo=None,
        limite_perdida=None,
        confianza=Decimal("0.60"),
        prioridad=1,
        justificacion="Señales mixtas.",
    )

    evidence_id = uuid4()

    evidence = SimpleNamespace(
        id=evidence_id,
        tipo_evidencia="MODELO",
        entidad_origen="ai.predicciones_activo",
        identificador_origen=None,
        descripcion="Predicción utilizada",
        valor_numerico=None,
        unidad=None,
        peso=Decimal("1"),
        contribucion="NEUTRAL",
        datos=None,
        fecha_evidencia=None,
        fecha_registro=datetime(
            2026,
            8,
            27,
            tzinfo=UTC,
        ),
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=analysis_request
        ),
        get_recommendation_by_request=AsyncMock(
            return_value=recommendation
        ),
        list_recommendation_assets=AsyncMock(
            return_value=[
                recommendation_asset
            ]
        ),
        list_analysis_evidence_for_recommendation=(
            AsyncMock(
                return_value=[evidence]
            )
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    result = (
        await service
        .get_user_recommendation_result(
            request_id=request_id,
            user_id=user_id,
        )
    )

    assert result.request_id == request_id
    assert (
        result.recommendation_id
        == recommendation_id
    )
    assert result.asset_id == asset_id
    assert result.type == "OBSERVAR"
    assert result.risk_level == "MEDIO"
    assert len(result.assets) == 1
    assert len(result.evidence) == 1

    assert (
        result.assets[0].action
        == "OBSERVAR"
    )
    assert (
        result.evidence[0].evidence_type
        == "MODELO"
    )

@pytest.mark.asyncio
async def test_rejects_unfinished_recommendation_result() -> None:
    request = SimpleNamespace(
        tipo_analisis="RECOMENDACION",
        estado="PENDIENTE",
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=request
        )
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotReadyError
    ):
        await service.get_user_recommendation_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )

@pytest.mark.asyncio
async def test_rejects_missing_persisted_recommendation() -> None:
    request = SimpleNamespace(
        tipo_analisis="RECOMENDACION",
        estado="COMPLETADA",
    )

    repository = SimpleNamespace(
        get_analysis_request_for_user=AsyncMock(
            return_value=request
        ),
        get_recommendation_by_request=AsyncMock(
            return_value=None
        ),
    )

    service = AnalysisRequestService(
        repository
    )

    with pytest.raises(
        AnalysisResultNotFoundError
    ):
        await service.get_user_recommendation_result(
            request_id=uuid4(),
            user_id=uuid4(),
        )

