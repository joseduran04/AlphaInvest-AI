import pytest

from alphainvest.modules.ai.application.price_forecast_horizon_comparison import (
    calculate_improvement,
)

pytestmark = pytest.mark.unit


def test_calculates_positive_improvement() -> None:
    result = calculate_improvement(
        baseline=4.0,
        candidate=3.0,
    )

    assert result == pytest.approx(25.0)


def test_calculates_negative_improvement() -> None:
    result = calculate_improvement(
        baseline=4.0,
        candidate=5.0,
    )

    assert result == pytest.approx(-25.0)


def test_handles_zero_baseline() -> None:
    result = calculate_improvement(
        baseline=0.0,
        candidate=1.0,
    )

    assert result == 0.0