from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.sentiment_analysis_processor import (
    SentimentAnalysisProcessor,
)
from alphainvest.modules.ai.domain.sentiment_enums import (
    SentimentClass,
)
from alphainvest.modules.ai.domain.sentiment_prediction import (
    SentimentPredictionProbabilities,
    SentimentPredictionResult,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_processes_pending_sentiment_request(
) -> None:
    request_id = uuid4()
    asset_id = uuid4()
    news_reference_id = uuid4()
    version_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        tipo_analisis="SENTIMIENTO",
        estado="PENDIENTE",
        parametros={
            "asset_id": str(
                asset_id
            ),
            "news_reference_id": str(
                news_reference_id
            ),
        },
    )

    news_reference = SimpleNamespace(
        id=news_reference_id,
        activo_id=asset_id,
        mongo_document_id="abc123",
        relevancia=Decimal("0.90"),
        idioma="en",
        fecha_publicacion=datetime(
            2026,
            8,
            27,
            tzinfo=UTC,
        ),
    )

    prediction = SentimentPredictionResult(
        version_id=version_id,
        model_id=uuid4(),
        model_version="0.1.0",
        classification=(
            SentimentClass.NEUTRAL
        ),
        confidence=Decimal("0.80"),
        probabilities=(
            SentimentPredictionProbabilities(
                negative=Decimal("0.10"),
                neutral=Decimal("0.80"),
                positive=Decimal("0.10"),
            )
        ),
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        get_sentiment_analysis_by_request_and_news=AsyncMock(
            return_value=None
        ),
        get_active_version_by_model_code=AsyncMock(
            return_value=SimpleNamespace(
                id=version_id
            )
        ),
        increment_analysis_request_attempt=AsyncMock(),
        update_analysis_request_status=AsyncMock(),
        commit=AsyncMock(),
    )

    market_repository = SimpleNamespace(
        get_news_reference=AsyncMock(
            return_value=news_reference
        )
    )

    mongo_repository = SimpleNamespace(
        get_by_document_id=AsyncMock(
            return_value={
                "title": "Financial title",
                "summary": (
                    "The company reported "
                    "quarterly results."
                ),
            }
        )
    )

    inference_service = SimpleNamespace(
        predict=AsyncMock(
            return_value=prediction
        )
    )

    persistence_service = SimpleNamespace(
        persist_news_analysis=AsyncMock()
    )

    processor = SentimentAnalysisProcessor(
        ai_repository=ai_repository,
        market_repository=market_repository,
        mongo_repository=mongo_repository,
        inference_service=inference_service,
        persistence_service=(
            persistence_service
        ),
    )

    await processor.process(
        request_id=request_id
    )

    ai_repository.increment_analysis_request_attempt.assert_awaited_once_with(
        request
    )

    assert (
        ai_repository
        .update_analysis_request_status
        .await_count
        == 3
    )

    inference_service.predict.assert_awaited_once_with(
        version_id=version_id,
        text=(
            "The company reported "
            "quarterly results."
        ),
    )

    persistence_service.persist_news_analysis.assert_awaited_once()

    assert (
        ai_repository.commit.await_count
        == 2
    )


@pytest.mark.asyncio
async def test_rejects_when_no_active_sentiment_version(
) -> None:
    request_id = uuid4()
    asset_id = uuid4()
    news_reference_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        tipo_analisis="SENTIMIENTO",
        estado="PENDIENTE",
        parametros={
            "asset_id": str(
                asset_id
            ),
            "news_reference_id": str(
                news_reference_id
            ),
        },
    )

    news_reference = SimpleNamespace(
        id=news_reference_id,
        activo_id=asset_id,
    )

    ai_repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        increment_analysis_request_attempt=AsyncMock(),
        update_analysis_request_status=AsyncMock(),
        commit=AsyncMock(),
        get_sentiment_analysis_by_request_and_news=AsyncMock(
            return_value=None
        ),
        get_active_version_by_model_code=AsyncMock(
            return_value=None
        ),
    )

    market_repository = SimpleNamespace(
        get_news_reference=AsyncMock(
            return_value=news_reference
        )
    )

    processor = SentimentAnalysisProcessor(
        ai_repository=ai_repository,
        market_repository=market_repository,
        mongo_repository=SimpleNamespace(),
        inference_service=SimpleNamespace(),
        persistence_service=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="versión activa",
    ):
        await processor.process(
            request_id=request_id
        )

    ai_repository.increment_analysis_request_attempt.assert_awaited_once_with(
        request
    )

    ai_repository.commit.assert_awaited_once()