from dataclasses import dataclass

from alphainvest.modules.ai.domain.ml_metrics import (
    RegressionMetrics,
)


@dataclass(frozen=True, slots=True)
class PriceForecastBaselineResult:
    """Resultado evaluado de un baseline de regresión."""

    algorithm: str
    training_rows: int
    validation_rows: int
    constant_prediction: float
    metrics: RegressionMetrics