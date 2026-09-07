import numpy as np

from alphainvest.modules.ai.application.regression_evaluator import (
    RegressionEvaluator,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLRegressionDataset,
)
from alphainvest.modules.ai.domain.price_forecast_baseline_result import (
    PriceForecastBaselineResult,
)


class PriceForecastBaselineService:
    """Evalúa baselines constantes para pronóstico."""

    @classmethod
    def evaluate_zero(
        cls,
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> PriceForecastBaselineResult:
        return cls._evaluate_constant(
            algorithm="ZERO_RETURN",
            constant=0.0,
            training=training,
            validation=validation,
        )

    @classmethod
    def evaluate_train_mean(
        cls,
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> PriceForecastBaselineResult:
        cls._validate_datasets(
            training=training,
            validation=validation,
        )

        constant = float(
            np.mean(training.targets)
        )

        return cls._evaluate_constant(
            algorithm="TRAIN_MEAN",
            constant=constant,
            training=training,
            validation=validation,
        )

    @classmethod
    def evaluate_train_median(
        cls,
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> PriceForecastBaselineResult:
        cls._validate_datasets(
            training=training,
            validation=validation,
        )

        constant = float(
            np.median(training.targets)
        )

        return cls._evaluate_constant(
            algorithm="TRAIN_MEDIAN",
            constant=constant,
            training=training,
            validation=validation,
        )

    @classmethod
    def _evaluate_constant(
        cls,
        *,
        algorithm: str,
        constant: float,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> PriceForecastBaselineResult:
        cls._validate_datasets(
            training=training,
            validation=validation,
        )

        predictions = np.full(
            validation.targets.shape,
            constant,
            dtype=np.float64,
        )

        metrics = RegressionEvaluator.evaluate(
            expected=validation.targets,
            predicted=predictions,
        )

        return PriceForecastBaselineResult(
            algorithm=algorithm,
            training_rows=training.rows,
            validation_rows=validation.rows,
            constant_prediction=constant,
            metrics=metrics,
        )

    @staticmethod
    def _validate_datasets(
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> None:
        if training.rows == 0:
            raise ValueError(
                "El conjunto de entrenamiento está vacío"
            )

        if validation.rows == 0:
            raise ValueError(
                "El conjunto de validación está vacío"
            )

        if (
            training.feature_names
            != validation.feature_names
        ):
            raise ValueError(
                "Train y validation deben utilizar "
                "las mismas features"
            )