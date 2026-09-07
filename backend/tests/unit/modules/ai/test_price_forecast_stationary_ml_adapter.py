from datetime import date
from decimal import Decimal
from uuid import uuid4

import numpy as np
import pytest

from alphainvest.modules.ai.application.price_forecast_stationary_ml_adapter import (
    PriceForecastStationaryMLAdapter,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTarget,
    PriceForecastTrainingRow,
)

pytestmark = pytest.mark.unit


def build_row() -> PriceForecastTrainingRow:
    asset_id = uuid4()

    features = AIFeatureRow(
        asset_id=asset_id,
        date=date(2026, 8, 10),
        close=Decimal("105"),
        volume=Decimal("1000000"),
        sma_20=Decimal("100"),
        ema_20=Decimal("102"),
        rsi_14=Decimal("60"),
        volatility_30=Decimal("0.25"),
        macd=Decimal("2"),
        macd_signal=Decimal("1.5"),
        macd_histogram=Decimal("0.5"),
    )

    target = PriceForecastTarget(
        base_date=date(2026, 8, 10),
        target_date=date(2026, 8, 17),
        base_price=Decimal("105"),
        target_price=Decimal("110"),
        future_return_percentage=Decimal("4.7619"),
    )

    return PriceForecastTrainingRow(
        features=features,
        target=target,
    )


def test_transforms_stationary_features() -> None:
    result = (
        PriceForecastStationaryMLAdapter
        .transform(
            (build_row(),)
        )
    )

    assert result.rows == 1
    assert result.columns == 9

    assert (
        result.feature_names
        == PriceForecastStationaryMLAdapter
        .FEATURE_NAMES
    )

    assert np.isfinite(
        result.features
    ).all()

    assert result.targets[0] == pytest.approx(
        4.7619
    )


def test_normalizes_price_levels() -> None:
    result = (
        PriceForecastStationaryMLAdapter
        .transform(
            (build_row(),)
        )
    )

    assert result.features[0, 0] == pytest.approx(
        5.0
    )

    assert result.features[0, 1] == pytest.approx(
        ((105 / 102) - 1) * 100
    )


def test_rejects_non_positive_close() -> None:
    row = build_row()

    invalid_features = AIFeatureRow(
        asset_id=row.features.asset_id,
        date=row.features.date,
        close=Decimal("0"),
        volume=row.features.volume,
        sma_20=row.features.sma_20,
        ema_20=row.features.ema_20,
        rsi_14=row.features.rsi_14,
        volatility_30=row.features.volatility_30,
        macd=row.features.macd,
        macd_signal=row.features.macd_signal,
        macd_histogram=row.features.macd_histogram,
    )

    invalid_row = PriceForecastTrainingRow(
        features=invalid_features,
        target=row.target,
    )

    with pytest.raises(ValueError):
        (
            PriceForecastStationaryMLAdapter
            .transform(
                (invalid_row,)
            )
        )