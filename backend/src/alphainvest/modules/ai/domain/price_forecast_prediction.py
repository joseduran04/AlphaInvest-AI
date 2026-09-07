from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PriceForecastPredictionResult:
    """Resultado de inferencia de precio."""

    asset_id: UUID
    base_date: date

    version_id: UUID
    model_id: UUID
    model_version: str

    horizon_sessions: int

    base_price: Decimal
    predicted_price: Decimal

    expected_return_percentage: Decimal

    source_name: str