from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.market.application.service import MarketService
from alphainvest.modules.market.domain.exceptions import AssetNotFoundError

pytestmark = pytest.mark.unit


def build_repository(closes: list[tuple[date, Decimal]]) -> SimpleNamespace:
    return SimpleNamespace(
        get_asset=AsyncMock(return_value=SimpleNamespace(moneda="USD")),
        list_daily_closes=AsyncMock(return_value=closes),
    )


@pytest.mark.asyncio
async def test_price_series_reports_change_over_period() -> None:
    asset_id = uuid4()
    repository = build_repository(
        [
            (date(2026, 9, 22), Decimal("736.60")),
            (date(2026, 9, 23), Decimal("744.10")),
            (date(2026, 9, 24), Decimal("770.815")),
        ]
    )

    series = await MarketService(repository).get_price_series(
        asset_id=asset_id,
        start_date=date(2026, 9, 22),
        max_points=800,
        preferred_source_name="Yahoo Finance",
    )

    assert len(series.points) == 3
    assert series.sampled is False
    assert series.change == Decimal("34.215")
    assert series.change_percentage == Decimal("4.6450")
    repository.list_daily_closes.assert_awaited_once_with(
        asset_id=asset_id,
        start_date=date(2026, 9, 22),
        preferred_source_name="Yahoo Finance",
    )


@pytest.mark.asyncio
async def test_price_series_is_sampled_keeping_first_and_last() -> None:
    start = date(1990, 1, 1)
    closes = [
        (start + timedelta(days=index), Decimal(index + 1))
        for index in range(5000)
    ]

    series = await MarketService(build_repository(closes)).get_price_series(
        asset_id=uuid4(),
        start_date=None,
        max_points=100,
        preferred_source_name="Yahoo Finance",
    )

    assert series.sampled is True
    assert len(series.points) <= 101
    assert series.points[0].close == Decimal("1")
    assert series.points[-1].close == Decimal("5000")


@pytest.mark.asyncio
async def test_price_series_empty_and_missing_asset() -> None:
    series = await MarketService(build_repository([])).get_price_series(
        asset_id=uuid4(),
        start_date=None,
        max_points=100,
        preferred_source_name="Yahoo Finance",
    )

    assert series.points == []
    assert series.change is None

    repository = SimpleNamespace(get_asset=AsyncMock(return_value=None))

    with pytest.raises(AssetNotFoundError):
        await MarketService(repository).get_price_series(
            asset_id=uuid4(),
            start_date=None,
            max_points=100,
            preferred_source_name="Yahoo Finance",
        )
