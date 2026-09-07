from dataclasses import dataclass

from alphainvest.modules.ai.domain.ml_metrics import (
    ClassificationMetrics,
)


@dataclass(frozen=True, slots=True)
class BaselineTrainingResult:
    """Resultado evaluado del baseline de tendencia."""

    algorithm: str
    training_rows: int
    validation_rows: int
    metrics: ClassificationMetrics