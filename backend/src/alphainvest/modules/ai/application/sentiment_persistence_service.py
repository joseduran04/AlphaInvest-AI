from datetime import datetime
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.sentiment_prediction import (
    SentimentPredictionResult,
)
from alphainvest.modules.ai.infrastructure.models import (
    SentimentAnalysisModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)


class SentimentPersistenceService:
    """Persiste resultados NLP de sentimiento."""

    SOURCE_TYPE_NEWS = "NOTICIA"

    def __init__(
        self,
        repository: AIRepository,
    ) -> None:
        self._repository = repository

    async def persist_news_analysis(
        self,
        *,
        request_id: UUID,
        asset_id: UUID,
        news_reference_id: UUID,
        mongo_document_id: str,
        prediction: SentimentPredictionResult,
        relevance: Decimal | None,
        language: str | None,
        summary: str | None,
        content_date: datetime | None,
    ) -> SentimentAnalysisModel:
        source_identifier = (
            mongo_document_id.strip()
        )

        if not source_identifier:
            raise ValueError(
                "El identificador MongoDB "
                "no puede estar vacío"
            )

        probabilities = (
            prediction.probabilities
        )

        score = (
            probabilities.positive
            - probabilities.negative
        )

        return (
            await self._repository
            .create_sentiment_analysis(
                request_id=request_id,
                asset_id=asset_id,
                news_reference_id=(
                    news_reference_id
                ),
                version_model_id=(
                    prediction.version_id
                ),
                source_type=(
                    self.SOURCE_TYPE_NEWS
                ),
                source_identifier=(
                    source_identifier
                ),
                sentiment=(
                    prediction
                    .classification
                    .value
                ),
                score=score,
                confidence=(
                    prediction.confidence
                ),
                positive_probability=(
                    probabilities.positive
                ),
                neutral_probability=(
                    probabilities.neutral
                ),
                negative_probability=(
                    probabilities.negative
                ),
                relevance=relevance,
                language=language,
                detected_entities=None,
                summary=summary,
                content_date=content_date,
            )
        )