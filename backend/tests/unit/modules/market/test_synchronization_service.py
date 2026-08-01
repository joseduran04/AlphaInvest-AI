from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError

from alphainvest.modules.market.application.synchronization_service import (
    PriceSynchronizationService,
)
from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    PriceSynchronizationError,
)
from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)

pytestmark = pytest.mark.unit


def build_price(
    price_date: date,
) -> DailyPricePoint:
    return DailyPricePoint(
        date=price_date,
        open=Decimal("210"),
        high=Decimal("215"),
        low=Decimal("208"),
        close=Decimal("214"),
        adjusted_close=None,
        volume=Decimal("1000"),
        currency="USD",
    )


@pytest.mark.asyncio
async def test_sync_raises_when_asset_missing() -> None:
    repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=None)
    )
    provider = SimpleNamespace(
        source_name="Alpha Vantage",
    )
    service = PriceSynchronizationService(
        repository=repository,
        provider=provider,
    )

    with pytest.raises(AssetNotFoundError):
        await service.synchronize_asset(
            asset_id=uuid4()
        )


@pytest.mark.asyncio
async def test_sync_raises_when_source_missing() -> None:
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=asset_id,
                simbolo="AAPL",
                moneda="USD",
            )
        ),
        get_financial_source_by_name=AsyncMock(
            return_value=None
        ),
    )
    provider = SimpleNamespace(
        source_name="Alpha Vantage",
    )
    service = PriceSynchronizationService(
        repository=repository,
        provider=provider,
    )

    with pytest.raises(FinancialSourceNotFoundError):
        await service.synchronize_asset(
            asset_id=asset_id
        )


@pytest.mark.asyncio
async def test_sync_creates_and_updates_prices() -> None:
    asset_id = uuid4()
    source_id = uuid4()
    first_date = date(2026, 7, 30)
    second_date = date(2026, 7, 31)
    synchronized_at = datetime.now(UTC)

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
        moneda="USD",
    )
    source = SimpleNamespace(
        id=source_id,
        nombre="Alpha Vantage",
    )
    prices = [
        build_price(first_date),
        build_price(second_date),
    ]

    repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=asset),
        get_financial_source_by_name=AsyncMock(
            return_value=source
        ),
        get_existing_price_dates=AsyncMock(
            return_value={first_date}
        ),
        upsert_daily_prices=AsyncMock(),
        mark_source_requested=AsyncMock(
            return_value=synchronized_at
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )
    provider = SimpleNamespace(
        source_name="Alpha Vantage",
        fetch_daily_prices=AsyncMock(
            return_value=prices
        ),
    )

    service = PriceSynchronizationService(
        repository=repository,
        provider=provider,
    )

    result = await service.synchronize_asset(
        asset_id=asset_id
    )

    assert result.received == 2
    assert result.created == 1
    assert result.updated == 1
    assert result.first_date == first_date
    assert result.last_date == second_date

    provider.fetch_daily_prices.assert_awaited_once_with(
        symbol="AAPL",
        currency="USD",
    )
    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_sync_rolls_back_database_error() -> None:
    asset_id = uuid4()
    source_id = uuid4()

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
        moneda="USD",
    )
    source = SimpleNamespace(
        id=source_id,
        nombre="Alpha Vantage",
    )
    prices = [
        build_price(date(2026, 7, 31))
    ]

    repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=asset),
        get_financial_source_by_name=AsyncMock(
            return_value=source
        ),
        get_existing_price_dates=AsyncMock(
            return_value=set()
        ),
        upsert_daily_prices=AsyncMock(
            side_effect=SQLAlchemyError("database error")
        ),
        mark_source_requested=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )
    provider = SimpleNamespace(
        source_name="Alpha Vantage",
        fetch_daily_prices=AsyncMock(
            return_value=prices
        ),
    )

    service = PriceSynchronizationService(
        repository=repository,
        provider=provider,
    )

    with pytest.raises(PriceSynchronizationError):
        await service.synchronize_asset(
            asset_id=asset_id
        )

    repository.rollback.assert_awaited_once()
    repository.commit.assert_not_awaited()