import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

from alphainvest.modules.ai.domain.ml_dataset import (
    FloatVector,
)
from alphainvest.modules.ai.domain.ml_metrics import (
    RegressionMetrics,
)


class RegressionEvaluator:
    """Calcula métricas de modelos de regresión."""

    @staticmethod
    def evaluate(
        *,
        expected: FloatVector,
        predicted: FloatVector,
    ) -> RegressionMetrics:
        if expected.shape != predicted.shape:
            raise ValueError(
                "Los vectores esperado y predicho "
                "deben tener la misma dimensión"
            )

        if expected.size == 0:
            raise ValueError(
                "No existen observaciones "
                "para evaluar"
            )

        if not np.isfinite(expected).all():
            raise ValueError(
                "Los valores esperados contienen "
                "elementos no finitos"
            )

        if not np.isfinite(predicted).all():
            raise ValueError(
                "Las predicciones contienen "
                "elementos no finitos"
            )

        squared_error = mean_squared_error(
            expected,
            predicted,
        )

        expected_direction = np.sign(
            expected
        )

        predicted_direction = np.sign(
            predicted
        )

        direction_accuracy = float(
            np.mean(
                expected_direction
                == predicted_direction
            )
        )

        return RegressionMetrics(
            mae=float(
                mean_absolute_error(
                    expected,
                    predicted,
                )
            ),
            rmse=float(
                np.sqrt(squared_error)
            ),
            r2=float(
                r2_score(
                    expected,
                    predicted,
                )
            ),
            direction_accuracy=direction_accuracy,
        )