from dataclasses import dataclass
from decimal import Decimal

from alphainvest.modules.ai.domain.trend_dataset import (
    TrendTrainingRow,
)


@dataclass(frozen=True, slots=True)
class TrendTemporalSplit:
    """Particiones cronológicas de un dataset de tendencia."""

    train_ratio: Decimal
    validation_ratio: Decimal
    test_ratio: Decimal
    purge_sessions: int

    train: tuple[TrendTrainingRow, ...]
    validation: tuple[TrendTrainingRow, ...]
    test: tuple[TrendTrainingRow, ...]

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