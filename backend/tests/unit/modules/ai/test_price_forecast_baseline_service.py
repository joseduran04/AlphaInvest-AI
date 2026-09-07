import numpy as np
import pytest

from alphainvest.modules.ai.application.price_forecast_baseline_service import (
    PriceForecastBaselineService,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLRegressionDataset,
)

pytestmark = pytest.mark.unit


FEATURE_NAMES = (
    "feature_1",
    "feature_2",
)


def build_dataset(
    targets: list[float],
) -> MLRegressionDataset:
    rows = len(targets)

    return MLRegressionDataset(
        feature_names=FEATURE_NAMES,
        features=np.ones(
            (rows, 2),
            dtype=np.float64,
        ),
        targets=np.asarray(
            targets,
            dtype=np.float64,
        ),
    )


def test_zero_baseline() -> None:
    training = build_dataset(
        [1.0, 2.0, 3.0]
    )

    validation = build_dataset(
        [1.0, -1.0]
    )

    result = (
        PriceForecastBaselineService
        .evaluate_zero(
            training=training,
            validation=validation,
        )
    )

    assert result.algorithm == "ZERO_RETURN"

    assert (
        result.constant_prediction
        == pytest.approx(0.0)
    )

    assert result.metrics.mae > 0


def test_train_mean_baseline() -> None:
    training = build_dataset(
        [1.0, 2.0, 3.0]
    )

    validation = build_dataset(
        [1.5, 2.5]
    )

    result = (
        PriceForecastBaselineService
        .evaluate_train_mean(
            training=training,
            validation=validation,
        )
    )

    assert result.algorithm == "TRAIN_MEAN"

    assert (
        result.constant_prediction
        == pytest.approx(2.0)
    )


def test_train_median_baseline() -> None:
    training = build_dataset(
        [-100.0, 1.0, 2.0]
    )

    validation = build_dataset(
        [1.0, 2.0]
    )

    result = (
        PriceForecastBaselineService
        .evaluate_train_median(
            training=training,
            validation=validation,
        )
    )

    assert result.algorithm == "TRAIN_MEDIAN"

    assert (
        result.constant_prediction
        == pytest.approx(1.0)
    )