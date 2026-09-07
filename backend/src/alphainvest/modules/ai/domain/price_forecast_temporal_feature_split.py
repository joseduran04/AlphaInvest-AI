from dataclasses import dataclass
from decimal import Decimal

from alphainvest.modules.ai.domain.price_forecast_temporal_feature_dataset import (
    PriceForecastTemporalFeatureRow,
)


@dataclass(frozen=True, slots=True)
class PriceForecastTemporalFeatureSplit:
    train_ratio: Decimal
    validation_ratio: Decimal
    test_ratio: Decimal

    purge_sessions: int

    train: tuple[
        PriceForecastTemporalFeatureRow,
        ...
    ]

    validation: tuple[
        PriceForecastTemporalFeatureRow,
        ...
    ]

    test: tuple[
        PriceForecastTemporalFeatureRow,
        ...
    ]

    @property
    def train_size(self) -> int:
        return len(self.train)

    @property
    def validation_size(self) -> int:
        return len(self.validation)

    @property
    def test_size(self) -> int:
        return len(self.test)