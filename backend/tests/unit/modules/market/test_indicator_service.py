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
    InvalidIndicatorParametersError,
)
from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
)
from alphainvest.modules.market.domain.indicator_values import (
    ClosingPricePoint,
)

pytestmark = pytest.mark.unit

SOURCE_ID = uuid4()
END = date(2026, 9, 25)


def build_prices(count: int) -> list[ClosingPricePoint]:
    return [
        ClosingPricePoint(
            date=END - timedelta(days=count - 1 - index),
            close=Decimal(100 + index),
        )
        for index in range(count)
    ]


def build_repository(
    prices: list[ClosingPricePoint],
) -> SimpleNamespace:
    return SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(id=uuid4(), simbolo="AAPL")
        ),
        get_indicator_price_source=AsyncMock(
            return_value=(SOURCE_ID, "Yahoo Finance")
        ),
        list_closing_prices_for_indicators=AsyncMock(
            return_value=prices
        ),
    )


async def list_indicators(
    repository: SimpleNamespace,
    **overrides: object,
) -> object:
    arguments: dict[str, object] = {
        "asset_id": uuid4(),
        "indicator_type": None,
        "period": None,
        "start_date": END - timedelta(days=9),
        "end_date": END,
        "limit": 500,
        "offset": 0,
        "preferred_source_name": "Yahoo Finance",
    }
    arguments.update(overrides)

    return await FinancialIndicatorService(
        repository  # type: ignore[arg-type]
    ).list_indicators(**arguments)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_rejects_missing_asset() -> None:
    repository = build_repository([])
    repository.get_asset = AsyncMock(return_value=None)

    with pytest.raises(AssetNotFoundError):
        await list_indicators(repository)


@pytest.mark.asyncio
async def test_computes_default_indicators_without_persisting() -> None:
    repository = build_repository(build_prices(120))

    response = await list_indicators(repository)

    types = {item.indicator_type for item in response.items}
    assert types == {
        FinancialIndicatorType.SMA,
        FinancialIndicatorType.EMA,
        FinancialIndicatorType.RSI,
        FinancialIndicatorType.VOLATILITY,
        FinancialIndicatorType.MACD,
        FinancialIndicatorType.MACD_SIGNAL,
        FinancialIndicatorType.MACD_HISTOGRAM,
    }
    # 10 días × 7 series, del más reciente al más antiguo.
    assert response.total == 70
    assert response.items[0].date == END
    assert response.items[-1].date == END - timedelta(days=9)
    assert not hasattr(repository, "upsert_financial_indicators")


@pytest.mark.asyncio
async def test_sma_value_matches_formula() -> None:
    repository = build_repository(build_prices(120))

    response = await list_indicators(
        repository,
        indicator_type=FinancialIndicatorType.SMA,
        period="20D",
    )

    latest = response.items[0]
    # Últimos 20 cierres: 200..219 → promedio 209.5.
    assert latest.date == END
    assert latest.value == Decimal("209.5")
    assert latest.period == "20D"
    assert response.total == 10


@pytest.mark.asyncio
async def test_macd_returns_its_three_series() -> None:
    repository = build_repository(build_prices(120))

    response = await list_indicators(
        repository,
        indicator_type=FinancialIndicatorType.MACD,
        period="12-26-9",
    )

    assert {item.indicator_type for item in response.items} == {
        FinancialIndicatorType.MACD,
        FinancialIndicatorType.MACD_SIGNAL,
        FinancialIndicatorType.MACD_HISTOGRAM,
    }


@pytest.mark.asyncio
async def test_loads_prices_with_warmup_before_window() -> None:
    repository = build_repository(build_prices(120))

    await list_indicators(
        repository,
        indicator_type=FinancialIndicatorType.RSI,
        period="14D",
    )

    call = repository.list_closing_prices_for_indicators.await_args
    start = END - timedelta(days=9)
    assert call.kwargs["since"] == start - timedelta(days=2 * 14 + 365)
    assert call.kwargs["until"] == END


@pytest.mark.asyncio
async def test_insufficient_history_returns_empty_list() -> None:
    repository = build_repository(build_prices(5))

    response = await list_indicators(repository)

    assert response.items == []
    assert response.total == 0


@pytest.mark.asyncio
async def test_asset_without_prices_returns_empty_list() -> None:
    repository = build_repository([])
    repository.get_indicator_price_source = AsyncMock(return_value=None)

    response = await list_indicators(repository)

    assert response.total == 0
    repository.list_closing_prices_for_indicators.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_period_that_does_not_match_type() -> None:
    repository = build_repository(build_prices(120))

    with pytest.raises(InvalidIndicatorParametersError):
        await list_indicators(
            repository,
            indicator_type=FinancialIndicatorType.SMA,
            period="12-26-9",
        )


@pytest.mark.asyncio
async def test_paginates_after_sorting() -> None:
    repository = build_repository(build_prices(120))

    response = await list_indicators(
        repository,
        indicator_type=FinancialIndicatorType.SMA,
        period="20D",
        limit=3,
        offset=3,
    )

    assert [item.date for item in response.items] == [
        END - timedelta(days=3),
        END - timedelta(days=4),
        END - timedelta(days=5),
    ]
    assert [item.id for item in response.items] == [4, 5, 6]
