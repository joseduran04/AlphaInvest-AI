import numpy as np
import pytest

from alphainvest.modules.ai.application.price_forecast_xgboost_service import (
    PriceForecastXGBoostService,
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
            float(index) * 0.1
            for index in range(rows)
        ],
        dtype=np.float64,
    )

    return MLRegressionDataset(
        feature_names=FEATURE_NAMES,
        features=features,
        targets=targets,
    )


def test_trains_and_evaluates_xgboost() -> None:
    training = build_dataset(
        rows=50
    )

    validation = build_dataset(
        rows=10
    )

    model, result = (
        PriceForecastXGBoostService
        .train_and_evaluate(
            training=training,
            validation=validation,
        )
    )

    assert model is not None

    assert (
        result.algorithm
        == "XGBOOST_REGRESSOR"
    )

    assert result.training_rows == 50
    assert result.validation_rows == 10

    assert result.metrics.mae >= 0
    assert result.metrics.rmse >= 0


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
            PriceForecastXGBoostService
            .train_and_evaluate(
                training=training,
                validation=validation,
            )
        )