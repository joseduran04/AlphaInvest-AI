import numpy as np
import pytest

from alphainvest.modules.ai.application.regression_evaluator import (
    RegressionEvaluator,
)

pytestmark = pytest.mark.unit


def test_calculates_regression_metrics() -> None:
    expected = np.asarray(
        [1.0, -2.0, 3.0],
        dtype=np.float64,
    )

    predicted = np.asarray(
        [1.5, -1.0, 2.0],
        dtype=np.float64,
    )

    metrics = RegressionEvaluator.evaluate(
        expected=expected,
        predicted=predicted,
    )

    assert metrics.mae > 0
    assert metrics.rmse > 0

    assert (
        metrics.direction_accuracy
        == pytest.approx(1.0)
    )


def test_detects_direction_errors() -> None:
    expected = np.asarray(
        [1.0, -1.0],
        dtype=np.float64,
    )

    predicted = np.asarray(
        [-1.0, -2.0],
        dtype=np.float64,
    )

    metrics = RegressionEvaluator.evaluate(
        expected=expected,
        predicted=predicted,
    )

    assert (
        metrics.direction_accuracy
        == pytest.approx(0.5)
    )


def test_rejects_different_shapes() -> None:
    expected = np.asarray(
        [1.0, 2.0],
        dtype=np.float64,
    )

    predicted = np.asarray(
        [1.0],
        dtype=np.float64,
    )

    with pytest.raises(ValueError):
        RegressionEvaluator.evaluate(
            expected=expected,
            predicted=predicted,
        )