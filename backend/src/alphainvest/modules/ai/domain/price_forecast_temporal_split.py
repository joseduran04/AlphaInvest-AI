from dataclasses import dataclass
from decimal import Decimal

from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTrainingRow,
)


@dataclass(frozen=True, slots=True)
class PriceForecastTemporalSplit:
    """Particiones cronológicas del dataset de regresión."""

    train_ratio: Decimal
    validation_ratio: Decimal
    test_ratio: Decimal

    purge_sessions: int

    train: tuple[
        PriceForecastTrainingRow,
        ...
    ]

    validation: tuple[
        PriceForecastTrainingRow,
        ...
    ]

    test: tuple[
        PriceForecastTrainingRow,
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

    @property
    def used_size(self) -> int:
        return (
            self.train_size
            + self.validation_size
            + self.test_size
        )