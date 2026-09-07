from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from alphainvest.modules.ai.application.trend_target_service import (
    TrendTargetService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)

pytestmark = pytest.mark.unit


def build_row(
    *,
    asset_id: UUID,
    row_date: date,
    close: Decimal,
) -> AIFeatureRow:
    return AIFeatureRow(
        asset_id=asset_id,
        date=row_date,
        close=close,
        volume=Decimal("1000"),
        sma_20=Decimal("100"),
        ema_20=Decimal("100"),
        rsi_14=Decimal("50"),
        volatility_30=Decimal("0.2"),
        macd=Decimal("1"),
        macd_signal=Decimal("0.8"),
        macd_histogram=Decimal("0.2"),
    )


def build_dataset(
    prices: list[Decimal],
) -> AIFeatureDataset:
    asset_id = uuid4()
    source_id = uuid4()
    start = date(2026, 1, 1)

    rows = tuple(
        build_row(
            asset_id=asset_id,
            row_date=start + timedelta(days=index),
            close=price,
        )
        for index, price in enumerate(prices)
    )

    return AIFeatureDataset(
        asset_id=asset_id,
        source_id=source_id,
        start_date=rows[0].date,
        end_date=rows[-1].date,
        rows=rows,
    )


def test_builds_future_targets() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("101"),
            Decimal("102"),
            Decimal("103"),
            Decimal("104"),
            Decimal("110"),
            Decimal("111"),
        ]
    )

    training = (
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=5,
            neutral_threshold_percentage=Decimal("1"),
        )
    )

    assert training.size == 2

    first = training.rows[0]

    assert first.target.base_price == Decimal("100")
    assert first.target.target_price == Decimal("110")
    assert first.target.base_date == dataset.rows[0].date
    assert first.target.target_date == dataset.rows[5].date
    assert (
        first.target.classification
        == TrendClassification.BULLISH
    )


def test_classifies_bullish() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("102"),
        ]
    )

    training = (
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("1"),
        )
    )

    assert (
        training.rows[0].target.classification
        == TrendClassification.BULLISH
    )


def test_classifies_bearish() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("98"),
        ]
    )

    training = (
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("1"),
        )
    )

    assert (
        training.rows[0].target.classification
        == TrendClassification.BEARISH
    )


def test_classifies_neutral() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("100.5"),
        ]
    )

    training = (
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("1"),
        )
    )

    assert (
        training.rows[0].target.classification
        == TrendClassification.NEUTRAL
    )


def test_threshold_boundary_is_neutral() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("101"),
        ]
    )

    training = (
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("1"),
        )
    )

    assert (
        training.rows[0].target.classification
        == TrendClassification.NEUTRAL
    )


def test_rejects_invalid_horizon() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("101"),
        ]
    )

    with pytest.raises(ValueError):
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=0,
            neutral_threshold_percentage=Decimal("1"),
        )


def test_rejects_negative_threshold() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("101"),
        ]
    )

    with pytest.raises(ValueError):
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("-1"),
        )


def test_rejects_horizon_larger_than_dataset() -> None:
    dataset = build_dataset(
        [
            Decimal("100"),
            Decimal("101"),
        ]
    )

    with pytest.raises(ValueError):
        TrendTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=2,
            neutral_threshold_percentage=Decimal("1"),
        )