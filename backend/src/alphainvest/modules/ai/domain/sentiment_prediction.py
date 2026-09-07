from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.sentiment_enums import (
    SentimentClass,
)


@dataclass(frozen=True, slots=True)
class SentimentPredictionProbabilities:
    negative: Decimal
    neutral: Decimal
    positive: Decimal

    @property
    def total(self) -> Decimal:
        return (
            self.negative
            + self.neutral
            + self.positive
        )


@dataclass(frozen=True, slots=True)
class SentimentPredictionResult:
    version_id: UUID
    model_id: UUID
    model_version: str

    classification: SentimentClass
    confidence: Decimal

    probabilities: SentimentPredictionProbabilities