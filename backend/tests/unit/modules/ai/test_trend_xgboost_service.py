import numpy as np
import pytest

from alphainvest.modules.ai.application.trend_xgboost_service import (
    TrendXGBoostService,
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
                [-4.0, -3.0],
                [-3.5, -3.5],
                [-3.0, -4.0],
                [-2.5, -3.0],
                [-3.0, -2.5],
                [0.0, 0.0],
                [0.2, -0.1],
                [-0.2, 0.1],
                [0.1, 0.2],
                [-0.1, -0.2],
                [3.0, 4.0],
                [3.5, 3.5],
                [4.0, 3.0],
                [2.5, 3.0],
                [3.0, 2.5],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [
                0,
                0,
                0,
                0,
                0,
                1,
                1,
                1,
                1,
                1,
                2,
                2,
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
                [-3.2, -3.1],
                [0.0, 0.1],
                [3.2, 3.1],
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


def test_trains_and_evaluates_xgboost() -> None:
    training = build_training_dataset()
    validation = build_validation_dataset()

    classifier, result = (
        TrendXGBoostService.train_and_evaluate(
            training=training,
            validation=validation,
        )
    )

    assert result.algorithm == "XGBOOST"
    assert result.training_rows == 15
    assert result.validation_rows == 3

    assert 0.0 <= result.metrics.accuracy <= 1.0
    assert (
        0.0
        <= result.metrics.balanced_accuracy
        <= 1.0
    )
    assert 0.0 <= result.metrics.macro_f1 <= 1.0

    predictions = classifier.predict(
        validation.features
    )

    assert len(predictions) == 3


def test_xgboost_predicts_probabilities() -> None:
    training = build_training_dataset()
    validation = build_validation_dataset()

    classifier, _ = (
        TrendXGBoostService.train_and_evaluate(
            training=training,
            validation=validation,
        )
    )

    probabilities = classifier.predict_proba(
        validation.features
    )

    assert probabilities.shape == (3, 3)

    assert np.allclose(
        probabilities.sum(axis=1),
        np.ones(3),
    )


def test_rejects_incompatible_features() -> None:
    training = build_training_dataset()

    validation = MLClassificationDataset(
        feature_names=("other",),
        features=np.asarray(
            [[1.0]],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [0],
            dtype=np.int64,
        ),
    )

    with pytest.raises(ValueError):
        TrendXGBoostService.train_and_evaluate(
            training=training,
            validation=validation,
        )


def test_rejects_missing_training_class() -> None:
    training = MLClassificationDataset(
        feature_names=FEATURE_NAMES,
        features=np.asarray(
            [
                [-1.0, -1.0],
                [0.0, 0.0],
                [1.0, 1.0],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [
                0,
                1,
                1,
            ],
            dtype=np.int64,
        ),
    )

    validation = build_validation_dataset()

    with pytest.raises(ValueError):
        TrendXGBoostService.train_and_evaluate(
            training=training,
            validation=validation,
        )