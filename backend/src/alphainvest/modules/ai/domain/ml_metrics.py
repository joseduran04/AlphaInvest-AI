from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClassificationMetrics:
    """Métricas de evaluación de un clasificador multiclase."""

    accuracy: float
    balanced_accuracy: float
    macro_f1: float
    confusion_matrix: tuple[
        tuple[int, ...],
        ...,
    ]


@dataclass(frozen=True, slots=True)
class RegressionMetrics:
    """Métricas para pronóstico continuo."""

    mae: float
    rmse: float
    r2: float
    direction_accuracy: float