from decimal import Decimal

import pytest

from alphainvest.modules.ai.domain.trend_experiment import (
    PREDICTION_TREND_V1,
    PREDICTION_TREND_YAHOO_V1,
)

pytestmark = pytest.mark.unit


def test_prediction_trend_v1_configuration() -> None:
    configuration = PREDICTION_TREND_V1

    assert configuration.horizon_sessions == 1

    assert (
        configuration.neutral_threshold_percentage
        == Decimal("0.5")
    )

    assert configuration.train_ratio == Decimal("0.70")
    assert configuration.validation_ratio == Decimal("0.15")
    assert configuration.test_ratio == Decimal("0.15")

    assert configuration.minimum_feature_rows == 35

def test_prediction_trend_yahoo_v1_configuration() -> None:
    configuration = PREDICTION_TREND_YAHOO_V1

    assert configuration.horizon_sessions == 5

    assert (
        configuration.neutral_threshold_percentage
        == Decimal("2.0")
    )

    assert configuration.train_ratio == Decimal("0.70")
    assert configuration.validation_ratio == Decimal("0.15")
    assert configuration.test_ratio == Decimal("0.15")

    assert configuration.minimum_feature_rows == 500