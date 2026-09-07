from dataclasses import dataclass
from uuid import UUID

from alphainvest.modules.ai.domain.price_forecast_prediction import (
    PriceForecastPredictionResult,
)
from alphainvest.modules.ai.domain.trend_prediction import (
    TrendPredictionResult,
)


@dataclass(frozen=True, slots=True)
class AssetAnalysisExecutionResult:
    """Resultado técnico compuesto de una solicitud ACTIVO."""

    request_id: UUID

    prediction: TrendPredictionResult

    price_forecast: (
        PriceForecastPredictionResult
        | None
    ) = None