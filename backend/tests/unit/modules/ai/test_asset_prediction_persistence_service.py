from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.asset_prediction_persistence_service import (
    AssetPredictionPersistenceService,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_persists_composed_asset_prediction() -> None:
    request_id = uuid4()
    asset_id = uuid4()
    trend_version_id = uuid4()
    price_version_id = uuid4()

    probabilities = SimpleNamespace(
        bullish=0.1069,
        neutral=0.2541,
        bearish=0.6389,
    )

    trend = SimpleNamespace(
        base_date=date(2026, 8, 14),
        version_id=trend_version_id,
        model_version="0.1.0",
        classification=SimpleNamespace(
            value="BAJISTA"
        ),
        confidence=0.6389,
        probabilities=probabilities,
    )

    price_forecast = SimpleNamespace(
        base_date=date(2026, 8, 14),
        version_id=price_version_id,
        model_version="0.1.0",
        horizon_sessions=5,
        base_price=Decimal(
            "305.92999268"
        ),
        predicted_price=Decimal(
            "308.21387360"
        ),
        expected_return_percentage=Decimal(
            "0.74653711"
        ),
        source_name="Yahoo Finance",
    )

    result = SimpleNamespace(
        prediction=trend,
        price_forecast=price_forecast,
    )

    persisted = SimpleNamespace(
        id=uuid4()
    )

    repository = SimpleNamespace(
        create_asset_prediction=AsyncMock(
            return_value=persisted
        )
    )

    calendar = Mock()

    calendar.target_session.return_value = date(
        2026,
        8,
        21,
    )

    service = AssetPredictionPersistenceService(
        repository=repository,
        trading_calendar=calendar,
    )

    response = await service.persist(
        request_id=request_id,
        asset_id=asset_id,
        market_code="NASDAQ",
        horizon="CORTO_PLAZO",
        result=result,
    )

    assert response is persisted

    calendar.target_session.assert_called_once_with(
        market_code="NASDAQ",
        base_date=date(2026, 8, 14),
        horizon_sessions=5,
    )

    repository.create_asset_prediction.assert_awaited_once()

    kwargs = (
        repository
        .create_asset_prediction
        .await_args
        .kwargs
    )

    assert kwargs["target_date"] == date(
        2026,
        8,
        21,
    )

    assert kwargs["trend"] == "BAJISTA"

    assert (
        kwargs["version_model_id"]
        == trend_version_id
    )