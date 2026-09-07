from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.integral_analysis_processor import (
    IntegralAnalysisProcessor,
)

pytestmark = pytest.mark.unit


def build_repository(
    *,
    integral_request: object,
) -> SimpleNamespace:
    return SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=integral_request
        ),
        get_analysis_request_for_user=AsyncMock(),
        get_asset_prediction_by_request=AsyncMock(),
        get_sentiment_analysis_by_request=AsyncMock(),
        get_recommendation_by_request=AsyncMock(),
        create_analysis_request=AsyncMock(),
        create_analysis_evidence=AsyncMock(),
        list_analysis_evidence_for_recommendation=AsyncMock(
            return_value=[]
        ),
        increment_analysis_request_attempt=AsyncMock(),
        update_analysis_request_status=AsyncMock(),
        update_analysis_request_parameters=AsyncMock(),
        commit=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_processes_integral_without_sentiment(
) -> None:
    integral_request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    recommendation_request_id = uuid4()
    recommendation_id = uuid4()

    integral_request = SimpleNamespace(
        id=integral_request_id,
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            29,
        ),
        portafolio_id=None,
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
            "sentiment_request_ids": [],
        },
    )

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=user_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    prediction = SimpleNamespace(
        id=uuid4(),
        activo_id=asset_id,
    )

    created_recommendation_request = (
        SimpleNamespace(
            id=recommendation_request_id
        )
    )

    recommendation_request_pending = (
        SimpleNamespace(
            id=recommendation_request_id,
            usuario_id=user_id,
            tipo_analisis="RECOMENDACION",
            estado="PENDIENTE",
        )
    )

    recommendation_request_completed = (
        SimpleNamespace(
            id=recommendation_request_id,
            usuario_id=user_id,
            tipo_analisis="RECOMENDACION",
            estado="COMPLETADA",
        )
    )

    recommendation = SimpleNamespace(
        id=recommendation_id
    )

    repository = build_repository(
        integral_request=integral_request
    )

    repository.get_analysis_request.side_effect = [
        integral_request,
        recommendation_request_pending,
        recommendation_request_completed,
    ]

    repository.get_analysis_request_for_user.return_value = (
        prediction_request
    )

    repository.get_asset_prediction_by_request.return_value = (
        prediction
    )

    repository.create_analysis_request.return_value = (
        created_recommendation_request
    )

    repository.get_recommendation_by_request.return_value = (
        recommendation
    )

    recommendation_processor = SimpleNamespace(
        process=AsyncMock()
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=(
            recommendation_processor
        ),
    )

    await processor.process(
        request_id=integral_request_id
    )

    repository.create_analysis_request.assert_awaited_once()

    create_call = (
        repository
        .create_analysis_request
        .await_args
    )

    assert create_call is not None

    assert (
        create_call.kwargs[
            "analysis_type"
        ]
        == "RECOMENDACION"
    )

    assert (
        create_call.kwargs[
            "parameters"
        ]["asset_id"]
        == str(asset_id)
    )

    assert (
        create_call.kwargs[
            "parameters"
        ]["prediction_request_id"]
        == str(prediction_request_id)
    )

    assert (
        create_call.kwargs[
            "parameters"
        ]["integral_request_id"]
        == str(integral_request_id)
    )

    (
        repository
        .update_analysis_request_parameters
        .assert_awaited_once()
    )

    recommendation_processor.process.assert_awaited_once_with(
        request_id=recommendation_request_id
    )

    repository.create_analysis_evidence.assert_not_awaited()

    assert (
        repository
        .update_analysis_request_status
        .await_count
        == 5
    )

    final_status_call = (
        repository
        .update_analysis_request_status
        .await_args
    )

    assert final_status_call is not None

    assert (
        final_status_call.kwargs["status"]
        == "COMPLETADA"
    )

    assert (
        final_status_call.kwargs["progress"]
        == Decimal("100")
    )


@pytest.mark.asyncio
async def test_processes_integral_with_sentiment(
) -> None:
    integral_request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    sentiment_request_id = uuid4()
    sentiment_analysis_id = uuid4()
    recommendation_request_id = uuid4()
    recommendation_id = uuid4()

    integral_request = SimpleNamespace(
        id=integral_request_id,
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            29,
        ),
        portafolio_id=None,
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
            "sentiment_request_ids": [
                str(sentiment_request_id)
            ],
        },
    )

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
        id=uuid4(),
        activo_id=asset_id,
    )

    sentiment_analysis = SimpleNamespace(
        id=sentiment_analysis_id,
        activo_id=asset_id,
        sentimiento="POSITIVO",
        puntuacion=Decimal("0.70"),
        confianza=Decimal("0.88"),
        relevancia=Decimal("0.95"),
        fecha_analisis=datetime(
            2026,
            8,
            29,
            tzinfo=UTC,
        ),
    )

    created_recommendation_request = (
        SimpleNamespace(
            id=recommendation_request_id
        )
    )

    recommendation_request_pending = (
        SimpleNamespace(
            id=recommendation_request_id,
            usuario_id=user_id,
            tipo_analisis="RECOMENDACION",
            estado="PENDIENTE",
        )
    )

    recommendation_request_completed = (
        SimpleNamespace(
            id=recommendation_request_id,
            usuario_id=user_id,
            tipo_analisis="RECOMENDACION",
            estado="COMPLETADA",
        )
    )

    recommendation = SimpleNamespace(
        id=recommendation_id
    )

    repository = build_repository(
        integral_request=integral_request
    )

    repository.get_analysis_request.side_effect = [
        integral_request,
        recommendation_request_pending,
        recommendation_request_completed,
    ]

    repository.get_analysis_request_for_user.side_effect = [
        prediction_request,
        sentiment_request,
    ]

    repository.get_asset_prediction_by_request.return_value = (
        prediction
    )

    repository.get_sentiment_analysis_by_request.return_value = (
        sentiment_analysis
    )

    repository.create_analysis_request.return_value = (
        created_recommendation_request
    )

    repository.get_recommendation_by_request.return_value = (
        recommendation
    )

    recommendation_processor = SimpleNamespace(
        process=AsyncMock()
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=(
            recommendation_processor
        ),
    )

    await processor.process(
        request_id=integral_request_id
    )

    repository.create_analysis_evidence.assert_awaited_once()

    evidence_call = (
        repository
        .create_analysis_evidence
        .await_args
    )

    assert evidence_call is not None

    assert (
        evidence_call.kwargs[
            "recommendation_id"
        ]
        == recommendation_id
    )

    assert (
        evidence_call.kwargs[
            "evidence_type"
        ]
        == "SENTIMIENTO"
    )

    assert (
        evidence_call.kwargs[
            "source_entity"
        ]
        == "ai.analisis_sentimiento"
    )

    assert (
        evidence_call.kwargs[
            "source_identifier"
        ]
        == str(sentiment_analysis_id)
    )

    assert (
        evidence_call.kwargs[
            "numeric_value"
        ]
        == Decimal("0.70")
    )

    assert (
        evidence_call.kwargs[
            "contribution"
        ]
        == "POSITIVA"
    )


@pytest.mark.asyncio
async def test_reuses_existing_recommendation_request(
) -> None:
    integral_request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    recommendation_request_id = uuid4()

    integral_request = SimpleNamespace(
        id=integral_request_id,
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            29,
        ),
        portafolio_id=None,
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
            "sentiment_request_ids": [],
            "recommendation_request_id": str(
                recommendation_request_id
            ),
        },
    )

    prediction_request = SimpleNamespace(
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    prediction = SimpleNamespace(
        activo_id=asset_id
    )

    recommendation_request = SimpleNamespace(
        id=recommendation_request_id,
        usuario_id=user_id,
        tipo_analisis="RECOMENDACION",
        estado="COMPLETADA",
    )

    recommendation = SimpleNamespace(
        id=uuid4()
    )

    repository = build_repository(
        integral_request=integral_request
    )

    repository.get_analysis_request.side_effect = [
        integral_request,
        recommendation_request,
    ]

    repository.get_analysis_request_for_user.return_value = (
        prediction_request
    )

    repository.get_asset_prediction_by_request.return_value = (
        prediction
    )

    repository.get_recommendation_by_request.return_value = (
        recommendation
    )

    recommendation_processor = SimpleNamespace(
        process=AsyncMock()
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=(
            recommendation_processor
        ),
    )

    await processor.process(
        request_id=integral_request_id
    )

    repository.create_analysis_request.assert_not_awaited()

    (
        repository
        .update_analysis_request_parameters
        .assert_not_awaited()
    )

    recommendation_processor.process.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_missing_integral_request(
) -> None:
    repository = build_repository(
        integral_request=None
    )

    repository.get_analysis_request.return_value = (
        None
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="no existe",
    ):
        await processor.process(
            request_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_non_integral_request(
) -> None:
    request = SimpleNamespace(
        tipo_analisis="ACTIVO",
        estado="PENDIENTE",
    )

    repository = build_repository(
        integral_request=request
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="INTEGRAL",
    ):
        await processor.process(
            request_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_non_pending_integral_request(
) -> None:
    request = SimpleNamespace(
        tipo_analisis="INTEGRAL",
        estado="COMPLETADA",
    )

    repository = build_repository(
        integral_request=request
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="PENDIENTE",
    ):
        await processor.process(
            request_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_integral_with_invalid_parameters(
) -> None:
    request = SimpleNamespace(
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        parametros=None,
    )

    repository = build_repository(
        integral_request=request
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="parámetros válidos",
    ):
        await processor.process(
            request_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_missing_asset_request(
) -> None:
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()

    request = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        portafolio_id=None,
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
    )

    repository = build_repository(
        integral_request=request
    )

    repository.get_analysis_request_for_user.return_value = (
        None
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="ACTIVO asociada.*no existe",
    ):
        await processor.process(
            request_id=request.id
        )


@pytest.mark.asyncio
async def test_rejects_incomplete_asset_request(
) -> None:
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()

    request = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        portafolio_id=None,
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
    )

    repository = build_repository(
        integral_request=request
    )

    repository.get_analysis_request_for_user.return_value = (
        SimpleNamespace(
            tipo_analisis="ACTIVO",
            estado="PENDIENTE",
        )
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="no está COMPLETADA",
    ):
        await processor.process(
            request_id=request.id
        )


@pytest.mark.asyncio
async def test_rejects_prediction_from_different_asset(
) -> None:
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()

    request = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        portafolio_id=None,
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
    )

    repository = build_repository(
        integral_request=request
    )

    repository.get_analysis_request_for_user.return_value = (
        SimpleNamespace(
            tipo_analisis="ACTIVO",
            estado="COMPLETADA",
        )
    )

    repository.get_asset_prediction_by_request.return_value = (
        SimpleNamespace(
            activo_id=uuid4()
        )
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="no pertenece",
    ):
        await processor.process(
            request_id=request.id
        )


@pytest.mark.asyncio
async def test_rejects_sentiment_from_different_asset(
) -> None:
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    sentiment_request_id = uuid4()

    request = SimpleNamespace(
        id=uuid4(),
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        portafolio_id=None,
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
    )

    prediction_request = SimpleNamespace(
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    sentiment_request = SimpleNamespace(
        tipo_analisis="SENTIMIENTO",
        estado="COMPLETADA",
    )

    repository = build_repository(
        integral_request=request
    )

    repository.get_analysis_request_for_user.side_effect = [
        prediction_request,
        sentiment_request,
    ]

    repository.get_asset_prediction_by_request.return_value = (
        SimpleNamespace(
            activo_id=asset_id
        )
    )

    repository.get_sentiment_analysis_by_request.return_value = (
        SimpleNamespace(
            activo_id=uuid4()
        )
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="SENTIMIENTO.*no pertenece",
    ):
        await processor.process(
            request_id=request.id
        )


@pytest.mark.asyncio
async def test_does_not_duplicate_existing_sentiment_evidence(
) -> None:
    integral_request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    sentiment_request_id = uuid4()
    sentiment_analysis_id = uuid4()
    recommendation_request_id = uuid4()
    recommendation_id = uuid4()

    integral_request = SimpleNamespace(
        id=integral_request_id,
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            29,
        ),
        portafolio_id=None,
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
            "sentiment_request_ids": [
                str(sentiment_request_id)
            ],
            "recommendation_request_id": str(
                recommendation_request_id
            ),
        },
    )

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
        id=uuid4(),
        activo_id=asset_id,
    )

    sentiment_analysis = SimpleNamespace(
        id=sentiment_analysis_id,
        activo_id=asset_id,
        sentimiento="NEUTRAL",
        puntuacion=Decimal("0.14"),
        confianza=Decimal("0.83"),
        relevancia=Decimal("1.00"),
        fecha_analisis=datetime(
            2026,
            8,
            29,
            tzinfo=UTC,
        ),
    )

    recommendation_request = SimpleNamespace(
        id=recommendation_request_id,
        usuario_id=user_id,
        tipo_analisis="RECOMENDACION",
        estado="COMPLETADA",
    )

    recommendation = SimpleNamespace(
        id=recommendation_id
    )

    existing_evidence = SimpleNamespace(
        tipo_evidencia="SENTIMIENTO",
        entidad_origen="ai.analisis_sentimiento",
        identificador_origen=str(
            sentiment_analysis_id
        ),
    )

    repository = build_repository(
        integral_request=integral_request
    )

    repository.get_analysis_request.side_effect = [
        integral_request,
        recommendation_request,
    ]

    repository.get_analysis_request_for_user.side_effect = [
        prediction_request,
        sentiment_request,
    ]

    repository.get_asset_prediction_by_request.return_value = (
        prediction
    )

    repository.get_sentiment_analysis_by_request.return_value = (
        sentiment_analysis
    )

    repository.get_recommendation_by_request.return_value = (
        recommendation
    )

    (
        repository
        .list_analysis_evidence_for_recommendation
        .return_value
    ) = [
        existing_evidence
    ]

    recommendation_processor = SimpleNamespace(
        process=AsyncMock()
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=(
            recommendation_processor
        ),
    )

    await processor.process(
        request_id=integral_request_id
    )

    (
        repository
        .list_analysis_evidence_for_recommendation
        .assert_awaited_once_with(
            recommendation_id=recommendation_id
        )
    )

    (
        repository
        .create_analysis_evidence
        .assert_not_awaited()
    )

    recommendation_processor.process.assert_not_awaited()

    final_status_call = (
        repository
        .update_analysis_request_status
        .await_args
    )

    assert final_status_call is not None

    assert (
        final_status_call.kwargs["status"]
        == "COMPLETADA"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "child_status",
    [
        "EJECUTANDO",
        "FALLIDA",
    ],
)
async def test_rejects_unfinished_existing_recommendation_request(
    child_status: str,
) -> None:
    integral_request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    prediction_request_id = uuid4()
    recommendation_request_id = uuid4()

    integral_request = SimpleNamespace(
        id=integral_request_id,
        usuario_id=user_id,
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        fecha_referencia=date(
            2026,
            8,
            29,
        ),
        portafolio_id=None,
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
            "sentiment_request_ids": [],
            "recommendation_request_id": str(
                recommendation_request_id
            ),
        },
    )

    prediction_request = SimpleNamespace(
        id=prediction_request_id,
        usuario_id=user_id,
        tipo_analisis="ACTIVO",
        estado="COMPLETADA",
    )

    prediction = SimpleNamespace(
        id=uuid4(),
        activo_id=asset_id,
    )

    recommendation_request = SimpleNamespace(
        id=recommendation_request_id,
        usuario_id=user_id,
        tipo_analisis="RECOMENDACION",
        estado=child_status,
    )

    repository = build_repository(
        integral_request=integral_request
    )

    repository.get_analysis_request.side_effect = [
        integral_request,
        recommendation_request,
    ]

    repository.get_analysis_request_for_user.return_value = (
        prediction_request
    )

    repository.get_asset_prediction_by_request.return_value = (
        prediction
    )

    recommendation_processor = SimpleNamespace(
        process=AsyncMock()
    )

    processor = IntegralAnalysisProcessor(
        ai_repository=repository,
        recommendation_processor=(
            recommendation_processor
        ),
    )

    with pytest.raises(
        ValueError,
        match="no finalizó correctamente",
    ):
        await processor.process(
            request_id=integral_request_id
        )

    recommendation_processor.process.assert_not_awaited()

    repository.create_analysis_request.assert_not_awaited()

    repository.create_analysis_evidence.assert_not_awaited()