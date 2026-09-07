import numpy as np
from sklearn.utils.class_weight import (
    compute_sample_weight,
)
from xgboost import XGBClassifier

from alphainvest.modules.ai.application.classification_evaluator import (
    ClassificationEvaluator,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLClassificationDataset,
)
from alphainvest.modules.ai.domain.xgboost_tuning import (
    XGBoostCandidate,
    XGBoostCandidateResult,
    XGBoostTuningResult,
)


class TrendXGBoostTuningService:
    """Compara una rejilla pequeña usando sólo validation."""

    CANDIDATES = (
        XGBoostCandidate(
            name="BASE_WEIGHTED",
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            use_balanced_weights=True,
        ),
        XGBoostCandidate(
            name="SHALLOW_WEIGHTED",
            n_estimators=80,
            max_depth=2,
            learning_rate=0.05,
            min_child_weight=1,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_alpha=0.1,
            reg_lambda=1.0,
            use_balanced_weights=True,
        ),
        XGBoostCandidate(
            name="SHALLOW_REGULARIZED",
            n_estimators=120,
            max_depth=2,
            learning_rate=0.03,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.5,
            reg_lambda=2.0,
            use_balanced_weights=True,
        ),
        XGBoostCandidate(
            name="DEPTH3_REGULARIZED",
            n_estimators=120,
            max_depth=3,
            learning_rate=0.03,
            min_child_weight=3,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.5,
            reg_lambda=2.0,
            use_balanced_weights=True,
        ),
        XGBoostCandidate(
            name="SHALLOW_UNWEIGHTED",
            n_estimators=80,
            max_depth=2,
            learning_rate=0.05,
            min_child_weight=1,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_alpha=0.1,
            reg_lambda=1.0,
            use_balanced_weights=False,
        ),
    )

    @classmethod
    def tune(
        cls,
        *,
        training: MLClassificationDataset,
        validation: MLClassificationDataset,
    ) -> XGBoostTuningResult:
        cls._validate(
            training=training,
            validation=validation,
        )

        results = tuple(
            cls._evaluate_candidate(
                candidate=candidate,
                training=training,
                validation=validation,
            )
            for candidate in cls.CANDIDATES
        )

        best = max(
            results,
            key=cls._selection_key,
        )

        return XGBoostTuningResult(
            candidates=results,
            best=best,
        )

    @staticmethod
    def build_classifier(
        candidate: XGBoostCandidate,
    ) -> XGBClassifier:
        return XGBClassifier(
            objective="multi:softprob",
            num_class=3,
            n_estimators=candidate.n_estimators,
            max_depth=candidate.max_depth,
            learning_rate=candidate.learning_rate,
            min_child_weight=(
                candidate.min_child_weight
            ),
            subsample=candidate.subsample,
            colsample_bytree=(
                candidate.colsample_bytree
            ),
            reg_alpha=candidate.reg_alpha,
            reg_lambda=candidate.reg_lambda,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=1,
            tree_method="hist",
        )

    @classmethod
    def _evaluate_candidate(
        cls,
        *,
        candidate: XGBoostCandidate,
        training: MLClassificationDataset,
        validation: MLClassificationDataset,
    ) -> XGBoostCandidateResult:
        classifier = cls.build_classifier(
            candidate
        )

        sample_weights = None

        if candidate.use_balanced_weights:
            sample_weights = compute_sample_weight(
                class_weight="balanced",
                y=training.targets,
            )

        classifier.fit(
            training.features,
            training.targets,
            sample_weight=sample_weights,
        )

        predicted_values = classifier.predict(
            validation.features
        )

        predictions = np.asarray(
            predicted_values,
            dtype=np.int64,
        )

        metrics = ClassificationEvaluator.evaluate(
            expected=validation.targets,
            predicted=predictions,
        )

        return XGBoostCandidateResult(
            candidate=candidate,
            metrics=metrics,
            predicted_classes=tuple(
                int(value)
                for value in predictions.tolist()
            ),
        )

    @staticmethod
    def _selection_key(
        result: XGBoostCandidateResult,
    ) -> tuple[float, float, int, float]:
        represented_classes = len(
            set(result.predicted_classes)
        )

        return (
            result.metrics.macro_f1,
            result.metrics.balanced_accuracy,
            represented_classes,
            result.metrics.accuracy,
        )

    @staticmethod
    def _validate(
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
                "Train y validation deben tener "
                "las mismas features"
            )

        classes = {
            int(value)
            for value in training.targets.tolist()
        }

        if classes != {0, 1, 2}:
            raise ValueError(
                "El entrenamiento requiere "
                "las tres clases"
            )