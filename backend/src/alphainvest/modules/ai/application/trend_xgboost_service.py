import numpy as np
from xgboost import XGBClassifier

from alphainvest.modules.ai.application.classification_evaluator import (
    ClassificationEvaluator,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLClassificationDataset,
)
from alphainvest.modules.ai.domain.xgboost_result import (
    XGBoostTrainingResult,
)


class TrendXGBoostService:
    """Entrena un clasificador XGBoost para tendencia."""

    ALGORITHM = "XGBOOST"

    @staticmethod
    def build_classifier() -> XGBClassifier:
        return XGBClassifier(
            objective="multi:softprob",
            num_class=3,
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            min_child_weight=2,
            reg_alpha=0.1,
            reg_lambda=1.0,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=1,
        )

    @classmethod
    def train_and_evaluate(
        cls,
        *,
        training: MLClassificationDataset,
        validation: MLClassificationDataset,
    ) -> tuple[
        XGBClassifier,
        XGBoostTrainingResult,
    ]:
        cls._validate_datasets(
            training=training,
            validation=validation,
        )

        classifier = cls.build_classifier()

        classifier.fit(
            training.features,
            training.targets,
        )

        prediction_values = classifier.predict(
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

        result = XGBoostTrainingResult(
            algorithm=cls.ALGORITHM,
            training_rows=training.rows,
            validation_rows=validation.rows,
            metrics=metrics,
        )

        return classifier, result

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

        if (
            training.feature_names
            != validation.feature_names
        ):
            raise ValueError(
                "Train y validation deben utilizar "
                "las mismas features"
            )

        training_classes = {
            int(value)
            for value in training.targets.tolist()
        }

        if training_classes != {0, 1, 2}:
            raise ValueError(
                "XGBoost requiere las tres clases "
                "de tendencia en entrenamiento"
            )