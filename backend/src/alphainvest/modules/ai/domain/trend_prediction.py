from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)


@dataclass(frozen=True, slots=True)
class TrendPredictionProbabilities:
    bearish: Decimal
    neutral: Decimal
    bullish: Decimal

    @property
    def total(self) -> Decimal:
        return (
            self.bearish
            + self.neutral
            + self.bullish
        )


@dataclass(frozen=True, slots=True)
class TrendPredictionResult:
    asset_id: UUID
    base_date: date

    version_id: UUID
    model_id: UUID
    model_version: str

    classification: TrendClassification
    confidence: Decimal

    probabilities: TrendPredictionProbabilities