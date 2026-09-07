from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)


@dataclass(frozen=True, slots=True)
class TrendTarget:
    """Target futuro asociado con una fila de features."""

    base_date: date
    target_date: date
    base_price: Decimal
    target_price: Decimal
    future_return_percentage: Decimal
    classification: TrendClassification


@dataclass(frozen=True, slots=True)
class TrendTrainingRow:
    """Fila supervisada para clasificación de tendencia."""

    features: AIFeatureRow
    target: TrendTarget


@dataclass(frozen=True, slots=True)
class TrendTrainingDataset:
    """Dataset supervisado de tendencia."""

    asset_id: UUID
    horizon_sessions: int
    neutral_threshold_percentage: Decimal
    rows: tuple[TrendTrainingRow, ...]

    @property
    def size(self) -> int:
        return len(self.rows)