from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.price_forecast_temporal_feature_service import (
    PriceForecastTemporalFeatureService,
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
    count: int,
) -> PriceForecastTrainingDataset:
    asset_id = uuid4()

    rows: list[
        PriceForecastTrainingRow
    ] = []

    start = date(2026, 1, 1)

    for index in range(count):
        row_date = (
            start
            + timedelta(days=index)
        )

        price = Decimal(
            str(100 + index)
        )

        features = AIFeatureRow(
            asset_id=asset_id,
            date=row_date,
            close=price,
            volume=Decimal(
                str(1000 + index)
            ),
            sma_20=price,
            ema_20=price,
            rsi_14=Decimal("50"),
            volatility_30=Decimal("0.2"),
            macd=Decimal("1"),
            macd_signal=Decimal("0.8"),
            macd_histogram=Decimal("0.2"),
        )

        target = PriceForecastTarget(
            base_date=row_date,
            target_date=(
                row_date
                + timedelta(days=5)
            ),
            base_price=price,
            target_price=price,
            future_return_percentage=(
                Decimal("0")
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
        horizon_sessions=5,
        rows=tuple(rows),
    )


def test_builds_temporal_features() -> None:
    source = build_dataset(
        50
    )

    result = (
        PriceForecastTemporalFeatureService
        .build_dataset(
            dataset=source
        )
    )

    assert result.lookback_sessions == 20

    assert result.size == 30

    first = result.rows[0]

    assert (
        first.features.date
        == source.rows[20].features.date
    )

    assert (
        first.return_1d_pct
        > Decimal("0")
    )

    assert (
        first.return_20d_pct
        > first.return_1d_pct
    )


def test_rejects_insufficient_history() -> None:
    source = build_dataset(
        20
    )

    with pytest.raises(ValueError):
        (
            PriceForecastTemporalFeatureService
            .build_dataset(
                dataset=source
            )
        )