from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from alphainvest.modules.ai.application.price_forecast_target_service import (
    PriceForecastTargetService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
    AIFeatureRow,
)

pytestmark = pytest.mark.unit


def build_row(
    *,
    asset_id: UUID,
    row_date: date,
    close: str,
) -> AIFeatureRow:
    return AIFeatureRow(
        asset_id=asset_id,
        date=row_date,
        close=Decimal(close),
        volume=Decimal("1000"),
        sma_20=Decimal("100"),
        ema_20=Decimal("100"),
        rsi_14=Decimal("50"),
        volatility_30=Decimal("0.20"),
        macd=Decimal("1"),
        macd_signal=Decimal("0.8"),
        macd_histogram=Decimal("0.2"),
    )


def test_builds_future_return_target() -> None:
    asset_id = uuid4()

    rows = (
        build_row(
            asset_id=asset_id,
            row_date=date(2026, 8, 10),
            close="100",
        ),
        build_row(
            asset_id=asset_id,
            row_date=date(2026, 8, 11),
            close="101",
        ),
        build_row(
            asset_id=asset_id,
            row_date=date(2026, 8, 12),
            close="105",
        ),
    )

    dataset = AIFeatureDataset(
        asset_id=asset_id,
        source_id=uuid4(),
        start_date=rows[0].date,
        end_date=rows[-1].date,
        rows=rows,
    )

    result = (
        PriceForecastTargetService
        .build_training_dataset(
            dataset=dataset,
            horizon_sessions=2,
        )
    )

    assert result.size == 1

    target = result.rows[0].target

    assert target.base_price == Decimal("100")
    assert target.target_price == Decimal("105")

    assert (
        target.future_return_percentage
        == Decimal("5.00")
    )


def test_rejects_invalid_horizon() -> None:
    asset_id = uuid4()

    row = build_row(
        asset_id=asset_id,
        row_date=date(2026, 8, 10),
        close="100",
    )

    dataset = AIFeatureDataset(
        asset_id=asset_id,
        source_id=uuid4(),
        start_date=row.date,
        end_date=row.date,
        rows=(row,),
    )

    with pytest.raises(ValueError):
        PriceForecastTargetService.build_training_dataset(
            dataset=dataset,
            horizon_sessions=0,
        )