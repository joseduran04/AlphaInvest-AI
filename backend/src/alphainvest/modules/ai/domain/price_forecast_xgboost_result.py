from dataclasses import dataclass

from alphainvest.modules.ai.domain.ml_metrics import (
    RegressionMetrics,
)


@dataclass(frozen=True, slots=True)
class PriceForecastXGBoostResult:
    """Resultado evaluado de XGBoost para regresión."""

    algorithm: str
    training_rows: int
    validation_rows: int
    metrics: RegressionMetrics