from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from alphainvest.modules.ai.application.trend_analysis_service import (
    TrendAnalysisService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_analysis import (
    TrendExperimentSpec,
)

pytestmark = pytest.mark.unit


def build_feature_row(
    *,
    asset_id: UUID,
    index: int,
    close: Decimal,
) -> AIFeatureRow:
    return AIFeatureRow(
        asset_id=asset_id,
        date=(
            date(2026, 1, 1)
            + timedelta(days=index)
        ),
        close=close,
        volume=Decimal("1000"),
        sma_20=Decimal("100"),
        ema_20=Decimal("100"),
        rsi_14=Decimal("50"),
        volatility_30=Decimal("0.20"),
        macd=Decimal("1"),
        macd_signal=Decimal("0.8"),
        macd_histogram=Decimal("0.2"),
    )


def build_feature_dataset() -> AIFeatureDataset:
    asset_id = uuid4()
    source_id = uuid4()

    prices = [
        Decimal(100 + (index % 7) - 3)
        for index in range(70)
    ]

    rows = tuple(
        build_feature_row(
            asset_id=asset_id,
            index=index,
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


def test_analyzes_class_distribution() -> None:
    dataset = build_feature_dataset()

    analysis = TrendAnalysisService.analyze(
        feature_dataset=dataset,
        specification=TrendExperimentSpec(
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("1"),
        ),
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
    )

    assert analysis.total_targets == 69

    assert (
        analysis.full_distribution.total
        == analysis.total_targets
    )

    assert (
        analysis.train_distribution.total
        + analysis.validation_distribution.total
        + analysis.test_distribution.total
        + analysis.total_purged
        == analysis.total_targets
    )


def test_distribution_percentages_sum_to_100() -> None:
    dataset = build_feature_dataset()

    analysis = TrendAnalysisService.analyze(
        feature_dataset=dataset,
        specification=TrendExperimentSpec(
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("1"),
        ),
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
    )

    distribution = analysis.full_distribution

    total_percentage = sum(
        (
            distribution.percentage(
                classification
            )
            for classification in (
                TrendClassification.BULLISH,
                TrendClassification.NEUTRAL,
                TrendClassification.BEARISH,
            )
        ),
        start=Decimal("0"),
    )

    assert total_percentage == Decimal("100")


def test_analyze_many_preserves_specifications() -> None:
    dataset = build_feature_dataset()

    specifications = (
        TrendExperimentSpec(
            horizon_sessions=1,
            neutral_threshold_percentage=Decimal("0.5"),
        ),
        TrendExperimentSpec(
            horizon_sessions=5,
            neutral_threshold_percentage=Decimal("1"),
        ),
    )

    analyses = TrendAnalysisService.analyze_many(
        feature_dataset=dataset,
        specifications=specifications,
        train_ratio=Decimal("0.70"),
        validation_ratio=Decimal("0.15"),
    )

    assert len(analyses) == 2

    assert (
        analyses[0].specification
        == specifications[0]
    )

    assert (
        analyses[1].specification
        == specifications[1]
    )


def test_rejects_empty_specifications() -> None:
    dataset = build_feature_dataset()

    with pytest.raises(ValueError):
        TrendAnalysisService.analyze_many(
            feature_dataset=dataset,
            specifications=(),
            train_ratio=Decimal("0.70"),
            validation_ratio=Decimal("0.15"),
        )