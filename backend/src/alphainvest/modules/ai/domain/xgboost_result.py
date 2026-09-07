from dataclasses import dataclass

from alphainvest.modules.ai.domain.ml_metrics import (
    ClassificationMetrics,
)


@dataclass(frozen=True, slots=True)
class XGBoostTrainingResult:
    """Resultado evaluado del clasificador XGBoost."""

    algorithm: str
    training_rows: int
    validation_rows: int
    metrics: ClassificationMetrics