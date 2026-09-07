from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.price_forecast_temporal_split_service import (
    PriceForecastTemporalSplitService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.price_forecast_dataset import (
    PriceForecastTarget,
    PriceForecastTrainingDataset,
    PriceForecastTrainingRow,
)

pytestmark = pytest.mark.unit


def build_dataset(
    *,
    count: int,
    horizon: int,
) -> PriceForecastTrainingDataset:
    asset_id = uuid4()
    start = date(2026, 1, 1)

    rows: list[
        PriceForecastTrainingRow
    ] = []

    for index in range(count):
        base_date = (
            start
            + timedelta(days=index)
        )

        target_date = (
            base_date
            + timedelta(days=horizon)
        )

        features = AIFeatureRow(
            asset_id=asset_id,
            date=base_date,
            close=Decimal("100"),
            volume=Decimal("1000"),
            sma_20=Decimal("100"),
            ema_20=Decimal("100"),
            rsi_14=Decimal("50"),
            volatility_30=Decimal("0.2"),
            macd=Decimal("1"),
            macd_signal=Decimal("0.8"),
            macd_histogram=Decimal("0.2"),
        )

        target = PriceForecastTarget(
            base_date=base_date,
            target_date=target_date,
            base_price=Decimal("100"),
            target_price=Decimal("101"),
            future_return_percentage=(
                Decimal("1")
            ),
        )

        rows.append(
            PriceForecastTrainingRow(
                features=features,
                target=target,
            )
        )

    return PriceForecastTrainingDataset(
        asset_id=asset_id,
        horizon_sessions=horizon,
        rows=tuple(rows),
    )


def test_splits_with_temporal_purge() -> None:
    dataset = build_dataset(
        count=100,
        horizon=5,
    )

    split = (
        PriceForecastTemporalSplitService
        .split(
            dataset=dataset,
            train_ratio=Decimal("0.70"),
            validation_ratio=Decimal("0.15"),
        )
    )

    assert split.purge_sessions == 5

    assert split.train_size > 0
    assert split.validation_size > 0
    assert split.test_size > 0

    assert (
        split.train[-1].target.target_date
        < split.validation[0].features.date
    )

    assert (
        split.validation[-1].target.target_date
        < split.test[0].features.date
    )


def test_rejects_invalid_ratios() -> None:
    dataset = build_dataset(
        count=100,
        horizon=5,
    )

    with pytest.raises(ValueError):
        (
            PriceForecastTemporalSplitService
            .split(
                dataset=dataset,
                train_ratio=Decimal("0.90"),
                validation_ratio=Decimal("0.20"),
            )
        )