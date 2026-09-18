from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.price_forecast_inference_service import (
    PriceForecastInferenceService,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_predicts_price_from_median_return() -> None:
    asset_id = uuid4()
    version_id = uuid4()
    source_id = uuid4()

    loaded = SimpleNamespace(
        version_id=version_id,
        model_id=uuid4(),
        version="0.1.0",
        horizon_sessions=5,
        median_return_percentage=(
            Decimal("0.7465371077185751")
        ),
        source_name="Yahoo Finance",
    )

    runtime_service = SimpleNamespace(
        load_version=AsyncMock(
            return_value=loaded
        )
    )

    price = SimpleNamespace(
        date=date(2026, 8, 14),
        close=Decimal("300"),
        adjusted_close=Decimal("305"),
    )

    history = SimpleNamespace(
        items=[price],
    )

    market_service = SimpleNamespace(
        get_asset_price_history=AsyncMock(
            return_value=history
        )
    )

    service = PriceForecastInferenceService(
        runtime_service=runtime_service,
        market_service=market_service,
    )

    reference_date = date(2026, 8, 14)

    result = await service.predict_latest(
        version_id=version_id,
        asset_id=asset_id,
        source_id=source_id,
        reference_date=reference_date,
    )

    market_service.get_asset_price_history.assert_awaited_once_with(
        asset_id=asset_id,
        start_date=None,
        end_date=reference_date,
        source_id=source_id,
        limit=1,
        offset=0,
    )

    expected = (
        Decimal("305")
        * (
            Decimal("1")
            + (
                Decimal(
                    "0.7465371077185751"
                )
                / Decimal("100")
            )
        )
    )

    assert result.base_price == Decimal("305")
    assert result.predicted_price == expected

    assert (
        result.expected_return_percentage
        == Decimal(
            "0.7465371077185751"
        )
    )

    assert result.horizon_sessions == 5