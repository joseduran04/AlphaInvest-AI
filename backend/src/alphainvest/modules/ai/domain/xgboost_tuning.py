from dataclasses import dataclass

from alphainvest.modules.ai.domain.ml_metrics import (
    ClassificationMetrics,
)


@dataclass(frozen=True, slots=True)
class XGBoostCandidate:
    """Configuración candidata de XGBoost."""

    name: str
    n_estimators: int
    max_depth: int
    learning_rate: float
    min_child_weight: float
    subsample: float
    colsample_bytree: float
    reg_alpha: float
    reg_lambda: float
    use_balanced_weights: bool


@dataclass(frozen=True, slots=True)
class XGBoostCandidateResult:
    """Evaluación de una configuración candidata."""

    candidate: XGBoostCandidate
    metrics: ClassificationMetrics
    predicted_classes: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class XGBoostTuningResult:
    """Resultado de la selección sobre validation."""

    candidates: tuple[XGBoostCandidateResult, ...]
    best: XGBoostCandidateResult