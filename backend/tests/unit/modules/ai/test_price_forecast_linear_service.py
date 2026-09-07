import numpy as np
import pytest

from alphainvest.modules.ai.application.price_forecast_linear_service import (
    PriceForecastLinearService,
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
    *,
    rows: int,
) -> MLRegressionDataset:
    features = np.asarray(
        [
            [
                float(index),
                float(index * 2),
            ]
            for index in range(rows)
        ],
        dtype=np.float64,
    )

    targets = np.asarray(
        [
            (float(index) * 0.1) + 0.5
            for index in range(rows)
        ],
        dtype=np.float64,
    )

    return MLRegressionDataset(
        feature_names=FEATURE_NAMES,
        features=features,
        targets=targets,
    )


def test_trains_ridge() -> None:
    training = build_dataset(
        rows=50
    )

    validation = build_dataset(
        rows=10
    )

    model, result = (
        PriceForecastLinearService
        .train_and_evaluate_ridge(
            training=training,
            validation=validation,
        )
    )

    assert model is not None
    assert result.algorithm == "RIDGE"

    assert result.metrics.mae >= 0
    assert result.metrics.rmse >= 0


def test_trains_huber() -> None:
    training = build_dataset(
        rows=50
    )

    validation = build_dataset(
        rows=10
    )

    model, result = (
        PriceForecastLinearService
        .train_and_evaluate_huber(
            training=training,
            validation=validation,
        )
    )

    assert model is not None

    assert (
        result.algorithm
        == "HUBER_REGRESSOR"
    )

    assert result.metrics.mae >= 0


def test_rejects_empty_training() -> None:
    training = MLRegressionDataset(
        feature_names=FEATURE_NAMES,
        features=np.empty(
            (0, 2),
            dtype=np.float64,
        ),
        targets=np.empty(
            0,
            dtype=np.float64,
        ),
    )

    validation = build_dataset(
        rows=10
    )

    with pytest.raises(ValueError):
        (
            PriceForecastLinearService
            .train_and_evaluate_ridge(
                training=training,
                validation=validation,
            )
        )