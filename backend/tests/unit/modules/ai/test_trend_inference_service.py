from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import numpy as np
import pytest

from alphainvest.modules.ai.application.trend_inference_service import (
    TrendInferenceService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
    AIFeatureRow,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_predicts_latest_trend() -> None:
    asset_id = uuid4()
    model_id = uuid4()
    version_id = uuid4()

    row = AIFeatureRow(
        asset_id=asset_id,
        date=date(2026, 8, 14),
        close=Decimal("305.93"),
        volume=Decimal("50000000"),
        sma_20=Decimal("300"),
        ema_20=Decimal("301"),
        rsi_14=Decimal("55"),
        volatility_30=Decimal("0.25"),
        macd=Decimal("1.2"),
        macd_signal=Decimal("1.0"),
        macd_histogram=Decimal("0.2"),
    )

    dataset = AIFeatureDataset(
        asset_id=asset_id,
        source_id=uuid4(),
        start_date=row.date,
        end_date=row.date,
        rows=(row,),
    )

    classifier = SimpleNamespace(
        predict_proba=lambda _: np.asarray(
            [[0.15, 0.25, 0.60]],
            dtype=np.float64,
        )
    )

    runtime_service = SimpleNamespace(
        load_version=AsyncMock(
            return_value=SimpleNamespace(
                version_id=version_id,
                model_id=model_id,
                version="0.1.0",
                classifier=classifier,
            )
        )
    )

    feature_service = SimpleNamespace(
        build_dataset=AsyncMock(
            return_value=dataset
        )
    )

    service = TrendInferenceService(
        runtime_service=runtime_service,
        feature_service=feature_service,
    )

    result = await service.predict_latest(
        version_id=version_id,
        asset_id=asset_id,
        start_date=date(2020, 1, 1),
        end_date=date(2026, 8, 14),
    )

    assert (
        result.classification
        == TrendClassification.BULLISH
    )

    assert result.confidence == Decimal("0.6")

    assert (
        result.probabilities.bearish
        == Decimal("0.15")
    )

    assert (
        result.probabilities.neutral
        == Decimal("0.25")
    )

    assert (
        result.probabilities.bullish
        == Decimal("0.6")
    )

    assert result.base_date == date(2026, 8, 14)
    assert result.version_id == version_id


@pytest.mark.asyncio
async def test_rejects_invalid_probability_shape() -> None:
    asset_id = uuid4()

    row = AIFeatureRow(
        asset_id=asset_id,
        date=date(2026, 8, 14),
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

    dataset = AIFeatureDataset(
        asset_id=asset_id,
        source_id=uuid4(),
        start_date=row.date,
        end_date=row.date,
        rows=(row,),
    )

    classifier = SimpleNamespace(
        predict_proba=lambda _: np.asarray(
            [[0.5, 0.5]],
            dtype=np.float64,
        )
    )

    runtime_service = SimpleNamespace(
        load_version=AsyncMock(
            return_value=SimpleNamespace(
                version_id=uuid4(),
                model_id=uuid4(),
                version="0.1.0",
                classifier=classifier,
            )
        )
    )

    feature_service = SimpleNamespace(
        build_dataset=AsyncMock(
            return_value=dataset
        )
    )

    service = TrendInferenceService(
        runtime_service=runtime_service,
        feature_service=feature_service,
    )

    with pytest.raises(ValueError):
        await service.predict_latest(
            version_id=uuid4(),
            asset_id=asset_id,
            start_date=date(2020, 1, 1),
            end_date=date(2026, 8, 14),
        )