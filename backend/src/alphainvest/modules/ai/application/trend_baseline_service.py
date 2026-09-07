import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from alphainvest.modules.ai.application.classification_evaluator import (
    ClassificationEvaluator,
)
from alphainvest.modules.ai.domain.baseline_result import (
    BaselineTrainingResult,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLClassificationDataset,
)


class TrendBaselineService:
    """Entrena el baseline lineal de clasificación de tendencia."""

    ALGORITHM = "LOGISTIC_REGRESSION"

    @staticmethod
    def build_pipeline() -> Pipeline:
        return Pipeline(
            steps=[
                (
                    "scaler",
                    StandardScaler(),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        solver="lbfgs",
                        class_weight="balanced",
                        max_iter=1000,
                    ),
                ),
            ]
        )

    @classmethod
    def train_and_evaluate(
        cls,
        *,
        training: MLClassificationDataset,
        validation: MLClassificationDataset,
    ) -> tuple[
        Pipeline,
        BaselineTrainingResult,
    ]:
        cls._validate_datasets(
            training=training,
            validation=validation,
        )

        pipeline = cls.build_pipeline()

        pipeline.fit(
            training.features,
            training.targets,
        )

        prediction_values = pipeline.predict(
            validation.features
        )

        predictions = np.asarray(
            prediction_values,
            dtype=np.int64,
        )

        metrics = ClassificationEvaluator.evaluate(
            expected=validation.targets,
            predicted=predictions,
        )

        result = BaselineTrainingResult(
            algorithm=cls.ALGORITHM,
            training_rows=training.rows,
            validation_rows=validation.rows,
            metrics=metrics,
        )

        return pipeline, result

    @staticmethod
    def _validate_datasets(
        *,
        training: MLClassificationDataset,
        validation: MLClassificationDataset,
    ) -> None:
        if training.rows == 0:
            raise ValueError(
                "El conjunto de entrenamiento está vacío"
            )

        if validation.rows == 0:
            raise ValueError(
                "El conjunto de validación está vacío"
            )

        if training.feature_names != validation.feature_names:
            raise ValueError(
                "Train y validation deben utilizar "
                "las mismas features"
            )

        training_classes = set(
            int(value)
            for value in training.targets.tolist()
        )

        if len(training_classes) < 2:
            raise ValueError(
                "El entrenamiento requiere al menos "
                "dos clases diferentes"
            )