from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from alphainvest.modules.ai.application.temporal_split_service import (
    TrendTemporalSplitService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_dataset import (
    TrendTarget,
    TrendTrainingDataset,
    TrendTrainingRow,
)

pytestmark = pytest.mark.unit


def build_training_row(
    *,
    asset_id: UUID,
    index: int,
    horizon: int,
) -> TrendTrainingRow:
    start = date(2026, 1, 1)

    base_date = (
        start + timedelta(days=index)
    )

    target_date = (
        start + timedelta(
            days=index + horizon
        )
    )

    features = AIFeatureRow(
        asset_id=asset_id,
        date=base_date,
        close=Decimal(100 + index),
        volume=Decimal("1000"),
        sma_20=Decimal("100"),
        ema_20=Decimal("100"),
        rsi_14=Decimal("50"),
        volatility_30=Decimal("0.20"),
        macd=Decimal("1"),
        macd_signal=Decimal("0.8"),
        macd_histogram=Decimal("0.2"),
    )

    target = TrendTarget(
        base_date=base_date,
        target_date=target_date,
        base_price=Decimal(100 + index),
        target_price=Decimal(
            100 + index + horizon
        ),
        future_return_percentage=Decimal("1"),
        classification=TrendClassification.BULLISH,
    )

    return TrendTrainingRow(
        features=features,
        target=target,
    )


def build_dataset(
    *,
    count: int,
    horizon: int,
) -> TrendTrainingDataset:
    asset_id = uuid4()

    rows = tuple(
        build_training_row(
            asset_id=asset_id,
            index=index,
            horizon=horizon,
        )
        for index in range(count)
    )

    return TrendTrainingDataset(
        asset_id=asset_id,
        horizon_sessions=horizon,
        neutral_threshold_percentage=Decimal("1"),
        rows=rows,
    )


def test_splits_dataset_chronologically() -> None:
    dataset = build_dataset(
        count=62,
        horizon=5,
    )

    split = TrendTemporalSplitService.split(
        dataset=dataset,
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
    )

    assert split.train_size == 36
    assert split.validation_size == 7
    assert split.test_size == 9

    assert (
        split.train[-1].features.date
        < split.validation[0].features.date
    )

    assert (
        split.validation[-1].features.date
        < split.test[0].features.date
    )


def test_applies_purge_between_partitions() -> None:
    dataset = build_dataset(
        count=62,
        horizon=5,
    )

    split = TrendTemporalSplitService.split(
        dataset=dataset,
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
    )

    assert (
        split.train[-1].target.target_date
        < split.validation[0].features.date
    )

    assert (
        split.validation[-1].target.target_date
        < split.test[0].features.date
    )


def test_preserves_total_used_rows() -> None:
    dataset = build_dataset(
        count=62,
        horizon=5,
    )

    split = TrendTemporalSplitService.split(
        dataset=dataset,
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
    )

    assert split.used_size == 52

    assert (
        split.used_size
        + (split.purge_sessions * 2)
        == dataset.size
    )


def test_calculates_test_ratio() -> None:
    dataset = build_dataset(
        count=62,
        horizon=5,
    )

    split = TrendTemporalSplitService.split(
        dataset=dataset,
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
    )

    assert split.test_ratio == Decimal("0.15")


@pytest.mark.parametrize(
    (
        "train_ratio",
        "validation_ratio",
    ),
    [
        (
            Decimal("0"),
            Decimal("0.15"),
        ),
        (
            Decimal("0.70"),
            Decimal("0"),
        ),
        (
            Decimal("0.90"),
            Decimal("0.10"),
        ),
        (
            Decimal("0.90"),
            Decimal("0.20"),
        ),
    ],
)
def test_rejects_invalid_ratios(
    train_ratio: Decimal,
    validation_ratio: Decimal,
) -> None:
    dataset = build_dataset(
        count=62,
        horizon=5,
    )

    with pytest.raises(ValueError):
        TrendTemporalSplitService.split(
            dataset=dataset,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
        )


def test_rejects_dataset_too_small_after_purge() -> None:
    dataset = build_dataset(
        count=11,
        horizon=5,
    )

    with pytest.raises(ValueError):
        TrendTemporalSplitService.split(
            dataset=dataset,
            train_ratio=Decimal("0.70"),
            validation_ratio=Decimal("0.15"),
        )