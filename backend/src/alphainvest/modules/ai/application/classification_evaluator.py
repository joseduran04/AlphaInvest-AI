import numpy as np
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)

from alphainvest.modules.ai.domain.ml_dataset import (
    IntegerVector,
)
from alphainvest.modules.ai.domain.ml_metrics import (
    ClassificationMetrics,
)


class ClassificationEvaluator:
    """Calcula métricas comunes para modelos multiclase."""

    CLASS_LABELS = (0, 1, 2)

    @classmethod
    def evaluate(
        cls,
        *,
        expected: IntegerVector,
        predicted: IntegerVector,
    ) -> ClassificationMetrics:
        if expected.shape != predicted.shape:
            raise ValueError(
                "Los vectores esperado y predicho "
                "deben tener la misma dimensión"
            )

        if expected.size == 0:
            raise ValueError(
                "No existen observaciones para evaluar"
            )

        matrix = confusion_matrix(
            expected,
            predicted,
            labels=cls.CLASS_LABELS,
        )

        return ClassificationMetrics(
            accuracy=float(
                accuracy_score(
                    expected,
                    predicted,
                )
            ),
            balanced_accuracy=float(
                balanced_accuracy_score(
                    expected,
                    predicted,
                )
            ),
            macro_f1=float(
                f1_score(
                    expected,
                    predicted,
                    labels=cls.CLASS_LABELS,
                    average="macro",
                    zero_division=0,
                )
            ),
            confusion_matrix=tuple(
                tuple(int(value) for value in row)
                for row in np.asarray(matrix)
            ),
        )