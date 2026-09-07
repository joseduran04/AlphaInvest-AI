from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.market.application.indicator_service import (
    FinancialIndicatorService,
)
from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    InsufficientPriceHistoryError,
)
from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
)
from alphainvest.modules.market.domain.indicator_values import (
    ClosingPricePoint,
)
from alphainvest.modules.market.presentation.schemas import (
    IndicatorCalculationRequest,
    IndicatorCalculationSpec,
)

pytestmark = pytest.mark.unit


def build_prices(
    count: int,
) -> list[ClosingPricePoint]:
    start = date(2026, 1, 1)

    return [
        ClosingPricePoint(
            date=start + timedelta(days=index),
            close=Decimal(100 + index),
        )
        for index in range(count)
    ]


@pytest.mark.asyncio
async def test_calculation_rejects_missing_asset() -> None:
    repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=None)
    )
    service = FinancialIndicatorService(repository)

    request = IndicatorCalculationRequest(
        source_id=uuid4(),
        calculations=[
            IndicatorCalculationSpec(
                indicator_type=(
                    FinancialIndicatorType.SMA
                ),
                period=20,
            )
        ],
    )

    with pytest.raises(AssetNotFoundError):
        await service.calculate_indicators(
            asset_id=uuid4(),
            request=request,
        )


@pytest.mark.asyncio
async def test_calculates_and_persists_sma() -> None:
    asset_id = uuid4()
    source_id = uuid4()

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
    )
    source = SimpleNamespace(
        id=source_id,
        nombre="Alpha Vantage",
        activa=True,
    )

    repository = SimpleNamespace(
        get_asset=AsyncMock(return_value=asset),
        get_financial_source=AsyncMock(
            return_value=source
        ),
        list_closing_prices_for_indicators=AsyncMock(
            return_value=build_prices(30)
        ),
        get_existing_indicator_keys=AsyncMock(
            return_value=set()
        ),
        upsert_financial_indicators=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = FinancialIndicatorService(repository)

    request = IndicatorCalculationRequest(
        source_id=source_id,
        calculations=[
            IndicatorCalculationSpec(
                indicator_type=(
                    FinancialIndicatorType.SMA
                ),
                period=20,
            )
        ],
    )

    response = await service.calculate_indicators(
        asset_id=asset_id,
        request=request,
    )

    assert response.total_calculated == 11
    assert response.total_created == 11
    assert response.total_updated == 0
    assert response.items[0].period == "20D"

    repository.upsert_financial_indicators.assert_awaited_once()
    repository.commit.assert_awaited_once()
    repository.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_counts_existing_indicators_as_updated() -> None:
    asset_id = uuid4()
    source_id = uuid4()
    prices = build_prices(5)

    existing_key = (
        FinancialIndicatorType.SMA.value,
        prices[2].date,
        "3D",
    )

    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=asset_id,
                simbolo="AAPL",
            )
        ),
        get_financial_source=AsyncMock(
            return_value=SimpleNamespace(
                id=source_id,
                nombre="Alpha Vantage",
                activa=True,
            )
        ),
        list_closing_prices_for_indicators=AsyncMock(
            return_value=prices
        ),
        get_existing_indicator_keys=AsyncMock(
            return_value={existing_key}
        ),
        upsert_financial_indicators=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = FinancialIndicatorService(repository)

    request = IndicatorCalculationRequest(
        source_id=source_id,
        calculations=[
            IndicatorCalculationSpec(
                indicator_type=(
                    FinancialIndicatorType.SMA
                ),
                period=3,
            )
        ],
    )

    response = await service.calculate_indicators(
        asset_id=asset_id,
        request=request,
    )

    assert response.total_calculated == 3
    assert response.total_created == 2
    assert response.total_updated == 1


@pytest.mark.asyncio
async def test_rejects_insufficient_history() -> None:
    asset_id = uuid4()
    source_id = uuid4()

    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=asset_id,
                simbolo="AAPL",
            )
        ),
        get_financial_source=AsyncMock(
            return_value=SimpleNamespace(
                id=source_id,
                nombre="Alpha Vantage",
                activa=True,
            )
        ),
        list_closing_prices_for_indicators=AsyncMock(
            return_value=build_prices(5)
        ),
    )

    service = FinancialIndicatorService(repository)

    request = IndicatorCalculationRequest(
        source_id=source_id,
        calculations=[
            IndicatorCalculationSpec(
                indicator_type=(
                    FinancialIndicatorType.SMA
                ),
                period=20,
            )
        ],
    )

    with pytest.raises(
        InsufficientPriceHistoryError
    ):
        await service.calculate_indicators(
            asset_id=asset_id,
            request=request,
        )

@pytest.mark.asyncio
async def test_calculates_and_persists_macd_series() -> None:
    asset_id = uuid4()
    source_id = uuid4()

    repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=asset_id,
                simbolo="AAPL",
            )
        ),
        get_financial_source=AsyncMock(
            return_value=SimpleNamespace(
                id=source_id,
                nombre="Alpha Vantage",
                activa=True,
            )
        ),
        list_closing_prices_for_indicators=AsyncMock(
            return_value=build_prices(40)
        ),
        get_existing_indicator_keys=AsyncMock(
            return_value=set()
        ),
        upsert_financial_indicators=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    service = FinancialIndicatorService(repository)

    request = IndicatorCalculationRequest(
        source_id=source_id,
        calculations=[
            IndicatorCalculationSpec(
                indicator_type=(
                    FinancialIndicatorType.MACD
                ),
                fast_period=3,
                slow_period=5,
                signal_period=3,
            )
        ],
    )

    response = await service.calculate_indicators(
        asset_id=asset_id,
        request=request,
    )

    assert response.total_calculated == 104
    assert response.total_created == 104
    assert response.total_updated == 0

    counts = {
        item.indicator_type: item.calculated
        for item in response.items
    }

    assert counts[
        FinancialIndicatorType.MACD
    ] == 36
    assert counts[
        FinancialIndicatorType.MACD_SIGNAL
    ] == 34
    assert counts[
        FinancialIndicatorType.MACD_HISTOGRAM
    ] == 34

    repository.upsert_financial_indicators.assert_awaited_once()
    repository.commit.assert_awaited_once()