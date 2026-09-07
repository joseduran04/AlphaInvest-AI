import numpy as np
import pytest

from alphainvest.modules.ai.application.trend_xgboost_tuning_service import (
    TrendXGBoostTuningService,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLClassificationDataset,
)

pytestmark = pytest.mark.unit


FEATURE_NAMES = (
    "feature_a",
    "feature_b",
)


def build_training() -> MLClassificationDataset:
    return MLClassificationDataset(
        feature_names=FEATURE_NAMES,
        features=np.asarray(
            [
                [-4.0, -3.0],
                [-3.5, -3.0],
                [-3.0, -4.0],
                [-2.8, -3.2],
                [0.0, 0.0],
                [0.2, 0.1],
                [-0.2, 0.1],
                [0.1, -0.2],
                [3.0, 4.0],
                [3.5, 3.0],
                [4.0, 3.0],
                [3.2, 3.4],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [
                0,
                0,
                0,
                0,
                1,
                1,
                1,
                1,
                2,
                2,
                2,
                2,
            ],
            dtype=np.int64,
        ),
    )


def build_validation() -> MLClassificationDataset:
    return MLClassificationDataset(
        feature_names=FEATURE_NAMES,
        features=np.asarray(
            [
                [-3.2, -3.3],
                [0.0, 0.1],
                [3.2, 3.3],
            ],
            dtype=np.float64,
        ),
        targets=np.asarray(
            [0, 1, 2],
            dtype=np.int64,
        ),
    )


def test_tunes_candidates() -> None:
    result = TrendXGBoostTuningService.tune(
        training=build_training(),
        validation=build_validation(),
    )

    assert len(result.candidates) == 5

    assert result.best in result.candidates

    assert (
        0.0
        <= result.best.metrics.macro_f1
        <= 1.0
    )


def test_candidate_names_are_unique() -> None:
    names = [
        candidate.name
        for candidate
        in TrendXGBoostTuningService.CANDIDATES
    ]

    assert len(names) == len(set(names))


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
            [0, 1, 1],
            dtype=np.int64,
        ),
    )

    with pytest.raises(ValueError):
        TrendXGBoostTuningService.tune(
            training=training,
            validation=build_validation(),
        )