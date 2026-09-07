from datetime import date
from decimal import Decimal
from uuid import uuid4

import numpy as np
import pytest

from alphainvest.modules.ai.application.trend_ml_adapter import (
    TrendMLAdapter,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_dataset import (
    TrendTarget,
    TrendTrainingRow,
)

pytestmark = pytest.mark.unit


def build_row(
    classification: TrendClassification,
) -> TrendTrainingRow:
    asset_id = uuid4()

    features = AIFeatureRow(
        asset_id=asset_id,
        date=date(2026, 1, 1),
        close=Decimal("100"),
        volume=Decimal("1000"),
        sma_20=Decimal("99"),
        ema_20=Decimal("99.5"),
        rsi_14=Decimal("55"),
        volatility_30=Decimal("0.25"),
        macd=Decimal("1.2"),
        macd_signal=Decimal("1.0"),
        macd_histogram=Decimal("0.2"),
    )

    target = TrendTarget(
        base_date=date(2026, 1, 1),
        target_date=date(2026, 1, 2),
        base_price=Decimal("100"),
        target_price=Decimal("101"),
        future_return_percentage=Decimal("1"),
        classification=classification,
    )

    return TrendTrainingRow(
        features=features,
        target=target,
    )


def test_transforms_rows_to_numeric_matrices() -> None:
    rows = (
        build_row(TrendClassification.BEARISH),
        build_row(TrendClassification.NEUTRAL),
        build_row(TrendClassification.BULLISH),
    )

    dataset = TrendMLAdapter.transform(rows)

    assert dataset.rows == 3
    assert dataset.columns == 9

    assert dataset.features.dtype == np.float64
    assert dataset.targets.dtype == np.int64

    assert dataset.targets.tolist() == [
        0,
        1,
        2,
    ]


def test_feature_names_have_stable_order() -> None:
    dataset = TrendMLAdapter.transform(
        (
            build_row(
                TrendClassification.BULLISH
            ),
        )
    )

    assert dataset.feature_names == (
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


def test_rejects_empty_rows() -> None:
    with pytest.raises(ValueError):
        TrendMLAdapter.transform(())