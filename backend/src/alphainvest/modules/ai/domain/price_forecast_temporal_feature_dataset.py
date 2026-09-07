from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTarget,
    PriceForecastTrainingRow,
)


@dataclass(frozen=True, slots=True)
class PriceForecastTemporalFeatureRow:
    """Fila supervisada con features temporales."""

    base_row: PriceForecastTrainingRow

    return_1d_pct: Decimal
    return_5d_pct: Decimal
    return_20d_pct: Decimal

    momentum_5_20_pct: Decimal

    volume_change_5d_pct: Decimal
    volume_change_20d_pct: Decimal

    @property
    def features(self) -> AIFeatureRow:
        return self.base_row.features

    @property
    def target(self) -> PriceForecastTarget:
        return self.base_row.target


@dataclass(frozen=True, slots=True)
class PriceForecastTemporalFeatureDataset:
    """Dataset supervisado con lookbacks históricos."""

    asset_id: UUID
    horizon_sessions: int
    lookback_sessions: int

    rows: tuple[
        PriceForecastTemporalFeatureRow,
        ...
    ]

    @property
    def size(self) -> int:
        return len(self.rows)