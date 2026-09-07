from decimal import Decimal

import pytest

from alphainvest.modules.ai.domain.price_forecast_experiment import (
    PRICE_FORECAST_YAHOO_V1,
)

pytestmark = pytest.mark.unit


def test_price_forecast_yahoo_v1() -> None:
    configuration = PRICE_FORECAST_YAHOO_V1

    assert configuration.horizon_sessions == 5

    assert (
        configuration.train_ratio
        == Decimal("0.70")
    )

    assert (
        configuration.validation_ratio
        == Decimal("0.15")
    )

    assert (
        configuration.test_ratio
        == Decimal("0.15")
    )

    assert configuration.minimum_feature_rows == 500