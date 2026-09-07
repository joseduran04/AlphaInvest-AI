from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AIFeatureRow:
    """Features técnicas de un activo para una fecha."""

    asset_id: UUID
    date: date
    close: Decimal
    volume: Decimal | None

    sma_20: Decimal
    ema_20: Decimal
    rsi_14: Decimal
    volatility_30: Decimal

    macd: Decimal
    macd_signal: Decimal
    macd_histogram: Decimal


@dataclass(frozen=True, slots=True)
class AIFeatureDataset:
    """Dataset técnico reproducible de un activo."""

    asset_id: UUID
    source_id: UUID
    start_date: date
    end_date: date
    rows: tuple[AIFeatureRow, ...]

    @property
    def size(self) -> int:
        return len(self.rows)