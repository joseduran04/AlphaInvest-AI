from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from alphainvest.modules.ai.application.asset_analysis_processor import (
    AssetAnalysisProcessor,
)
from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisRequestStatus,
)
from alphainvest.modules.ai.domain.exceptions import (
    AnalysisRequestInvalidParametersError,
    AnalysisRequestInvalidStateError,
    AnalysisRequestNotFoundError,
    AnalysisRequestProcessingError,
    AnalysisRequestUnsupportedError,
)

pytestmark = pytest.mark.unit


def build_request() -> SimpleNamespace:
    asset_id = uuid4()

    return SimpleNamespace(
        id=uuid4(),
        tipo_analisis="ACTIVO",
        horizonte="CORTO_PLAZO",
        estado="PENDIENTE",
        fecha_referencia=date(2026, 8, 14),
        parametros={
            "asset_id": str(asset_id),
        },
        porcentaje_progreso=Decimal("0"),
        mensaje_error=None,
    )


@pytest.mark.asyncio
async def test_processes_pending_asset_request() -> None:
    request = build_request()
    version_id = uuid4()

    prediction = SimpleNamespace(
        classification="BAJISTA"
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        update_analysis_request_status=AsyncMock(
            return_value=request
        ),
        increment_analysis_request_attempt=AsyncMock(
            return_value=1
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    inference_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=prediction
        )
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=inference_service,
    )

    result = await processor.process(
        request_id=request.id,
        version_id=version_id,
    )

    repository.increment_analysis_request_attempt.assert_awaited_once_with(
        request
    )

    assert result.request_id == request.id
    assert result.prediction is prediction

    assert (
        repository
        .update_analysis_request_status
        .await_count
        == 2
    )

    assert repository.commit.await_count == 2

    inference_service.predict_latest.assert_awaited_once()


@pytest.mark.asyncio
async def test_rejects_missing_request() -> None:
    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=None
        )
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=SimpleNamespace(),
    )

    with pytest.raises(
        AnalysisRequestNotFoundError
    ):
        await processor.process(
            request_id=uuid4(),
            version_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_rejects_non_pending_request() -> None:
    request = build_request()
    request.estado = "COMPLETADA"

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        )
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=SimpleNamespace(),
    )

    with pytest.raises(
        AnalysisRequestInvalidStateError
    ):
        await processor.process(
            request_id=request.id,
            version_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_rejects_wrong_analysis_type() -> None:
    request = build_request()
    request.tipo_analisis = "PORTAFOLIO"

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        )
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=SimpleNamespace(),
    )

    with pytest.raises(
        AnalysisRequestUnsupportedError
    ):
        await processor.process(
            request_id=request.id,
            version_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_rejects_unsupported_horizon() -> None:
    request = build_request()
    request.horizonte = "LARGO_PLAZO"

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        )
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=SimpleNamespace(),
    )

    with pytest.raises(
        AnalysisRequestUnsupportedError
    ):
        await processor.process(
            request_id=request.id,
            version_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_rejects_invalid_asset_id() -> None:
    request = build_request()

    request.parametros = {
        "asset_id": "invalid-uuid"
    }

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        )
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=SimpleNamespace(),
    )

    with pytest.raises(
        AnalysisRequestInvalidParametersError
    ):
        await processor.process(
            request_id=request.id,
            version_id=uuid4(),
        )


@pytest.mark.asyncio
async def test_marks_request_failed_when_inference_fails() -> None:
    request = build_request()

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        update_analysis_request_status=AsyncMock(
            return_value=request
        ),
        increment_analysis_request_attempt=AsyncMock(
            return_value=1
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    inference_service = SimpleNamespace(
        predict_latest=AsyncMock(
            side_effect=RuntimeError(
                "Inference failure"
            )
        )
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=inference_service,
    )

    with pytest.raises(
        AnalysisRequestProcessingError
    ):
        await processor.process(
            request_id=request.id,
            version_id=uuid4(),
        )

    assert (
        repository
        .update_analysis_request_status
        .await_count
        == 2
    )

    assert repository.commit.await_count == 2

    repository.rollback.assert_awaited_once()

    assert (
        repository.get_analysis_request.await_count
        == 2
    )

    failed_call = (
        repository
        .update_analysis_request_status
        .await_args_list[-1]
    )

    assert (
        failed_call.kwargs["status"]
        == "FALLIDA"
    )


@pytest.mark.asyncio
async def test_processes_trend_and_price_forecast() -> None:
    request = build_request()

    trend_prediction = SimpleNamespace(
        asset_id=uuid4(),
    )

    price_prediction = SimpleNamespace(
        asset_id=trend_prediction.asset_id,
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        update_analysis_request_status=AsyncMock(
            return_value=request
        ),
        increment_analysis_request_attempt=AsyncMock(
            return_value=1
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    inference_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=trend_prediction
        )
    )

    price_forecast_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=price_prediction
        )
    )

    asset = SimpleNamespace(
        mercado=SimpleNamespace(
            codigo="NASDAQ"
        )
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    persistence_service = SimpleNamespace(
        persist=AsyncMock()
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=inference_service,
        price_forecast_service=(
            price_forecast_service
        ),
        market_repository=market_repository,
        prediction_persistence_service=(
            persistence_service
        ),
    )

    price_version_id = uuid4()
    source_id = uuid4()

    result = await processor.process(
        request_id=request.id,
        version_id=uuid4(),
        price_forecast_version_id=(
            price_version_id
        ),
        price_source_id=source_id,
    )

    assert result.prediction is trend_prediction

    assert (
        result.price_forecast
        is price_prediction
    )

    price_forecast_service.predict_latest.assert_awaited_once_with(
        version_id=price_version_id,
        asset_id=UUID(
            request.parametros["asset_id"]
        ),
        source_id=source_id,
    )

    market_repository.get_asset.assert_awaited_once_with(
        UUID(
            request.parametros["asset_id"]
        )
    )

    persistence_service.persist.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolves_runtime_automatically() -> None:
    request = build_request()

    trend_version_id = uuid4()
    price_version_id = uuid4()
    source_id = uuid4()

    runtime = SimpleNamespace(
        trend_version_id=trend_version_id,
        price_forecast_version_id=(
            price_version_id
        ),
        price_source_id=source_id,
    )

    runtime_service = SimpleNamespace(
        resolve=AsyncMock(
            return_value=runtime
        )
    )

    trend_prediction = SimpleNamespace()

    price_prediction = SimpleNamespace()

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        update_analysis_request_status=AsyncMock(
            return_value=request
        ),
        increment_analysis_request_attempt=AsyncMock(
            return_value=1
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    inference_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=trend_prediction
        )
    )

    price_forecast_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=price_prediction
        )
    )

    asset = SimpleNamespace(
        mercado=SimpleNamespace(
            codigo="NASDAQ"
        )
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    persistence_service = SimpleNamespace(
        persist=AsyncMock()
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=inference_service,
        price_forecast_service=(
            price_forecast_service
        ),
        runtime_service=runtime_service,
        market_repository=market_repository,
        prediction_persistence_service=(
            persistence_service
        ),
    )

    result = await processor.process(
        request_id=request.id
    )

    runtime_service.resolve.assert_awaited_once()

    inference_service.predict_latest.assert_awaited_once()

    price_forecast_service.predict_latest.assert_awaited_once_with(
        version_id=price_version_id,
        asset_id=UUID(
            request.parametros["asset_id"]
        ),
        source_id=source_id,
    )

    assert result.prediction is trend_prediction

    assert (
        result.price_forecast
        is price_prediction
    )

    market_repository.get_asset.assert_awaited_once_with(
        UUID(
            request.parametros["asset_id"]
        )
    )

    persistence_service.persist.assert_awaited_once()


@pytest.mark.asyncio
async def test_persists_composed_prediction_before_completion() -> None:
    request = build_request()

    trend_version_id = uuid4()
    price_version_id = uuid4()
    source_id = uuid4()

    runtime = SimpleNamespace(
        trend_version_id=trend_version_id,
        price_forecast_version_id=(
            price_version_id
        ),
        price_source_id=source_id,
    )

    runtime_service = SimpleNamespace(
        resolve=AsyncMock(
            return_value=runtime
        )
    )

    trend_prediction = SimpleNamespace(
        base_date=date(2026, 8, 14),
    )

    price_prediction = SimpleNamespace(
        base_date=date(2026, 8, 14),
    )

    asset = SimpleNamespace(
        id=UUID(
            request.parametros["asset_id"]
        ),
        mercado=SimpleNamespace(
            codigo="NASDAQ"
        ),
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        update_analysis_request_status=AsyncMock(
            return_value=request
        ),
        increment_analysis_request_attempt=AsyncMock(
            return_value=1
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    inference_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=trend_prediction
        )
    )

    price_forecast_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=price_prediction
        )
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    persistence_service = SimpleNamespace(
        persist=AsyncMock()
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=inference_service,
        price_forecast_service=(
            price_forecast_service
        ),
        runtime_service=runtime_service,
        market_repository=market_repository,
        prediction_persistence_service=(
            persistence_service
        ),
    )

    result = await processor.process(
        request_id=request.id
    )

    persistence_service.persist.assert_awaited_once()

    kwargs = (
        persistence_service
        .persist
        .await_args
        .kwargs
    )

    assert kwargs["request_id"] == request.id

    assert kwargs["asset_id"] == asset.id

    assert kwargs["market_code"] == "NASDAQ"

    assert (
        kwargs["horizon"]
        == "CORTO_PLAZO"
    )

    assert (
        kwargs["result"].prediction
        is trend_prediction
    )

    assert (
        kwargs["result"].price_forecast
        is price_prediction
    )

    assert result.prediction is trend_prediction

    assert (
        result.price_forecast
        is price_prediction
    )


@pytest.mark.asyncio
async def test_marks_failed_when_prediction_persistence_fails() -> None:
    request = build_request()

    runtime = SimpleNamespace(
        trend_version_id=uuid4(),
        price_forecast_version_id=uuid4(),
        price_source_id=uuid4(),
    )

    runtime_service = SimpleNamespace(
        resolve=AsyncMock(
            return_value=runtime
        )
    )

    inference_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=SimpleNamespace(
                base_date=date(2026, 8, 14),
            )
        )
    )

    price_forecast_service = SimpleNamespace(
        predict_latest=AsyncMock(
            return_value=SimpleNamespace(
                base_date=date(2026, 8, 14),
            )
        )
    )

    asset = SimpleNamespace(
        mercado=SimpleNamespace(
            codigo="NASDAQ"
        )
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        )
    )

    persistence_service = SimpleNamespace(
        persist=AsyncMock(
            side_effect=RuntimeError(
                "Prediction insert failure"
            )
        )
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            side_effect=[
                request,
                request,
            ]
        ),
        update_analysis_request_status=AsyncMock(
            return_value=request
        ),
        increment_analysis_request_attempt=AsyncMock(
            return_value=1
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    processor = AssetAnalysisProcessor(
        repository=repository,
        inference_service=inference_service,
        price_forecast_service=(
            price_forecast_service
        ),
        runtime_service=runtime_service,
        market_repository=market_repository,
        prediction_persistence_service=(
            persistence_service
        ),
    )

    with pytest.raises(
        AnalysisRequestProcessingError
    ):
        await processor.process(
            request_id=request.id
        )

    repository.rollback.assert_awaited()

    status_calls = (
        repository
        .update_analysis_request_status
        .await_args_list
    )

    assert (
        status_calls[-1].kwargs["status"]
        == AnalysisRequestStatus.FAILED.value
    )

    