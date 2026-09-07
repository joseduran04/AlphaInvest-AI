from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.sentiment_persistence_service import (
    SentimentPersistenceService,
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
async def test_persists_news_sentiment(
) -> None:
    request_id = uuid4()
    asset_id = uuid4()
    news_reference_id = uuid4()
    version_id = uuid4()

    prediction = SentimentPredictionResult(
        version_id=version_id,
        model_id=uuid4(),
        model_version="0.1.0",
        classification=(
            SentimentClass.POSITIVE
        ),
        confidence=Decimal("0.80"),
        probabilities=(
            SentimentPredictionProbabilities(
                negative=Decimal("0.10"),
                neutral=Decimal("0.10"),
                positive=Decimal("0.80"),
            )
        ),
    )

    persisted = SimpleNamespace(
        id=uuid4()
    )

    repository = SimpleNamespace(
        create_sentiment_analysis=AsyncMock(
            return_value=persisted
        )
    )

    service = (
        SentimentPersistenceService(
            repository
        )
    )

    result = (
        await service
        .persist_news_analysis(
            request_id=request_id,
            asset_id=asset_id,
            news_reference_id=(
                news_reference_id
            ),
            mongo_document_id="abc123",
            prediction=prediction,
            relevance=Decimal("0.95"),
            language="en",
            summary="Financial summary",
            content_date=datetime(
                2026,
                8,
                27,
                tzinfo=UTC,
            ),
        )
    )

    assert result is persisted

    call = (
        repository
        .create_sentiment_analysis
        .await_args
    )

    assert call is not None

    kwargs = call.kwargs

    assert (
        kwargs["version_model_id"]
        == version_id
    )

    assert (
        kwargs["source_type"]
        == "NOTICIA"
    )

    assert (
        kwargs["source_identifier"]
        == "abc123"
    )

    assert (
        kwargs["sentiment"]
        == "POSITIVO"
    )

    assert (
        kwargs["score"]
        == Decimal("0.70")
    )

    assert (
        kwargs["positive_probability"]
        == Decimal("0.80")
    )

    assert (
        kwargs["neutral_probability"]
        == Decimal("0.10")
    )

    assert (
        kwargs["negative_probability"]
        == Decimal("0.10")
    )


@pytest.mark.asyncio
async def test_rejects_empty_mongo_identifier(
) -> None:
    repository = SimpleNamespace(
        create_sentiment_analysis=AsyncMock()
    )

    service = (
        SentimentPersistenceService(
            repository
        )
    )

    prediction = SentimentPredictionResult(
        version_id=uuid4(),
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

    with pytest.raises(
        ValueError,
        match="MongoDB",
    ):
        await service.persist_news_analysis(
            request_id=uuid4(),
            asset_id=uuid4(),
            news_reference_id=uuid4(),
            mongo_document_id="   ",
            prediction=prediction,
            relevance=None,
            language=None,
            summary=None,
            content_date=None,
        )

    repository.create_sentiment_analysis.assert_not_awaited()