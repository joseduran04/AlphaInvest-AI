from dataclasses import dataclass

from alphainvest.modules.ai.domain.ml_metrics import (
    RegressionMetrics,
)


@dataclass(frozen=True, slots=True)
class PriceForecastRegressionResult:
    """Resultado evaluado de un regresor de pronóstico."""

    algorithm: str
    training_rows: int
    validation_rows: int
    metrics: RegressionMetrics