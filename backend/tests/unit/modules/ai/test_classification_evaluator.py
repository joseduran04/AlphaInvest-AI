import numpy as np
import pytest

from alphainvest.modules.ai.application.classification_evaluator import (
    ClassificationEvaluator,
)

pytestmark = pytest.mark.unit


def test_evaluates_perfect_predictions() -> None:
    expected = np.asarray(
        [0, 1, 2, 0, 1, 2],
        dtype=np.int64,
    )

    predicted = np.asarray(
        [0, 1, 2, 0, 1, 2],
        dtype=np.int64,
    )

    metrics = ClassificationEvaluator.evaluate(
        expected=expected,
        predicted=predicted,
    )

    assert metrics.accuracy == 1.0
    assert metrics.balanced_accuracy == 1.0
    assert metrics.macro_f1 == 1.0

    assert metrics.confusion_matrix == (
        (2, 0, 0),
        (0, 2, 0),
        (0, 0, 2),
    )


def test_confusion_matrix_always_contains_three_classes() -> None:
    expected = np.asarray(
        [0, 0, 2, 2],
        dtype=np.int64,
    )

    predicted = np.asarray(
        [0, 2, 2, 2],
        dtype=np.int64,
    )

    metrics = ClassificationEvaluator.evaluate(
        expected=expected,
        predicted=predicted,
    )

    assert len(metrics.confusion_matrix) == 3

    assert all(
        len(row) == 3
        for row in metrics.confusion_matrix
    )


def test_rejects_different_vector_shapes() -> None:
    expected = np.asarray(
        [0, 1],
        dtype=np.int64,
    )

    predicted = np.asarray(
        [0],
        dtype=np.int64,
    )

    with pytest.raises(ValueError):
        ClassificationEvaluator.evaluate(
            expected=expected,
            predicted=predicted,
        )


def test_rejects_empty_evaluation() -> None:
    empty = np.asarray(
        [],
        dtype=np.int64,
    )

    with pytest.raises(ValueError):
        ClassificationEvaluator.evaluate(
            expected=empty,
            predicted=empty,
        )