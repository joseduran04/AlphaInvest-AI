from datetime import date
from decimal import Decimal
from uuid import uuid4

import numpy as np
import pytest

from alphainvest.modules.ai.application.price_forecast_ml_adapter import (
    PriceForecastMLAdapter,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTarget,
    PriceForecastTrainingRow,
)

pytestmark = pytest.mark.unit


def test_transforms_regression_dataset() -> None:
    asset_id = uuid4()

    features = AIFeatureRow(
        asset_id=asset_id,
        date=date(2026, 8, 10),
        close=Decimal("100"),
        volume=Decimal("1000"),
        sma_20=Decimal("99"),
        ema_20=Decimal("98"),
        rsi_14=Decimal("55"),
        volatility_30=Decimal("0.20"),
        macd=Decimal("1.2"),
        macd_signal=Decimal("1"),
        macd_histogram=Decimal("0.2"),
    )

    target = PriceForecastTarget(
        base_date=date(2026, 8, 10),
        target_date=date(2026, 8, 17),
        base_price=Decimal("100"),
        target_price=Decimal("105"),
        future_return_percentage=Decimal("5"),
    )

    row = PriceForecastTrainingRow(
        features=features,
        target=target,
    )

    result = PriceForecastMLAdapter.transform(
        (row,)
    )

    assert result.rows == 1
    assert result.columns == 9

    assert result.targets.dtype == np.float64

    assert result.targets[0] == pytest.approx(
        5.0
    )

    assert result.feature_names == (
        "close",
        "volume",
        "sma_20",
        "ema_20",
        "rsi_14",
        "volatility_30",
        "macd",
        "macd_signal",
        "macd_histogram",
    )