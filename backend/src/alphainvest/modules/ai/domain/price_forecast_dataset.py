from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)


@dataclass(frozen=True, slots=True)
class PriceForecastTarget:
    """Target futuro para regresión de precio."""

    base_date: date
    target_date: date

    base_price: Decimal
    target_price: Decimal

    future_return_percentage: Decimal


@dataclass(frozen=True, slots=True)
class PriceForecastTrainingRow:
    """Fila supervisada para pronóstico de rendimiento."""

    features: AIFeatureRow
    target: PriceForecastTarget


@dataclass(frozen=True, slots=True)
class PriceForecastTrainingDataset:
    """Dataset supervisado para regresión."""

    asset_id: UUID
    horizon_sessions: int

    rows: tuple[
        PriceForecastTrainingRow,
        ...
    ]

    @property
    def size(self) -> int:
        return len(self.rows)