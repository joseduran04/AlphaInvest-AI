from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.asset_analysis_runtime_service import (
    AssetAnalysisRuntimeService,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_resolves_asset_analysis_runtime() -> None:
    trend_model = SimpleNamespace(
        id=uuid4(),
    )

    price_model = SimpleNamespace(
        id=uuid4(),
    )

    trend_version = SimpleNamespace(
        id=uuid4(),
        version="0.1.0",
    )

    price_version = SimpleNamespace(
        id=uuid4(),
        version="0.1.0",
    )

    source = SimpleNamespace(
        id=uuid4(),
        nombre="Yahoo Finance",
    )

    ai_repository = SimpleNamespace(
        get_model_by_code=AsyncMock(
            side_effect=[
                trend_model,
                price_model,
            ]
        ),
        list_model_versions=AsyncMock(
            side_effect=[
                [trend_version],
                [price_version],
            ]
        ),
    )

    market_repository = SimpleNamespace(
        get_financial_source_by_name=AsyncMock(
            return_value=source
        )
    )

    service = AssetAnalysisRuntimeService(
        ai_repository=ai_repository,
        market_repository=market_repository,
    )

    result = await service.resolve()

    assert (
        result.trend_version_id
        == trend_version.id
    )

    assert (
        result.price_forecast_version_id
        == price_version.id
    )

    assert result.price_source_id == source.id

    assert result.trend_version == "0.1.0"

    assert (
        result.price_forecast_version
        == "0.1.0"
    )

    assert (
        result.price_source_name
        == "Yahoo Finance"
    )