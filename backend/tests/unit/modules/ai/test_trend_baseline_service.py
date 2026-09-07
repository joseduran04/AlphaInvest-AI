import numpy as np
import pytest

from alphainvest.modules.ai.application.trend_baseline_service import (
    TrendBaselineService,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLClassificationDataset,
)

pytestmark = pytest.mark.unit


FEATURE_NAMES = (
    "feature_a",
    "feature_b",
)


def build_training_dataset() -> MLClassificationDataset:
    return MLClassificationDataset(
        feature_names=FEATURE_NAMES,
        features=np.asarray(
            [
                [-3.0, -2.0],
                [-2.5, -2.5],
                [-2.0, -3.0],
                [0.0, 0.0],
                [0.1, -0.1],
                [-0.1, 0.1],
                [2.0, 3.0],
                [2.5, 2.5],
                [3.0, 2.0],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [
                0,
                0,
                0,
                1,
                1,
                1,
                2,
                2,
                2,
            ],
            dtype=np.int64,
        ),
    )


def build_validation_dataset() -> MLClassificationDataset:
    return MLClassificationDataset(
        feature_names=FEATURE_NAMES,
        features=np.asarray(
            [
                [-2.2, -2.4],
                [0.0, 0.1],
                [2.3, 2.2],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [
                0,
                1,
                2,
            ],
            dtype=np.int64,
        ),
    )


def test_trains_and_evaluates_baseline() -> None:
    training = build_training_dataset()
    validation = build_validation_dataset()

    pipeline, result = (
        TrendBaselineService.train_and_evaluate(
            training=training,
            validation=validation,
        )
    )

    assert result.algorithm == "LOGISTIC_REGRESSION"
    assert result.training_rows == 9
    assert result.validation_rows == 3

    assert 0.0 <= result.metrics.accuracy <= 1.0

    assert (
        0.0
        <= result.metrics.balanced_accuracy
        <= 1.0
    )

    assert 0.0 <= result.metrics.macro_f1 <= 1.0

    predictions = pipeline.predict(
        validation.features
    )

    assert len(predictions) == 3


def test_rejects_incompatible_features() -> None:
    training = build_training_dataset()

    validation = MLClassificationDataset(
        feature_names=("other",),
        features=np.asarray(
            [
                [1.0],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [0],
            dtype=np.int64,
        ),
    )

    with pytest.raises(ValueError):
        TrendBaselineService.train_and_evaluate(
            training=training,
            validation=validation,
        )


def test_rejects_single_class_training() -> None:
    training = MLClassificationDataset(
        feature_names=FEATURE_NAMES,
        features=np.asarray(
            [
                [1.0, 1.0],
                [2.0, 2.0],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [2, 2],
            dtype=np.int64,
        ),
    )

    validation = build_validation_dataset()

    with pytest.raises(ValueError):
        TrendBaselineService.train_and_evaluate(
            training=training,
            validation=validation,
        )