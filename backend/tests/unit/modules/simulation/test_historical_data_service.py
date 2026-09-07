from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.application.historical_data_service import (
    HistoricalDataService,
)
from alphainvest.modules.simulation.domain.exceptions import (
    SimulationHistoricalPriceNotFoundError,
    SimulationHistoricalSourceUnavailableError,
)

pytestmark = pytest.mark.unit


def build_repository(
    *,
    source: object | None,
    prices: list[object] | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        get_financial_source_by_name=AsyncMock(
            return_value=source
        ),
        list_asset_prices_for_simulation=AsyncMock(
            return_value=prices or []
        ),
    )


@pytest.mark.asyncio
async def test_load_asset_history_uses_adjusted_close(
) -> None:
    source = SimpleNamespace(id=uuid4())

    repository = build_repository(
        source=source,
        prices=[
            SimpleNamespace(
                fecha=date(2024, 1, 2),
                cierre=Decimal("100"),
                cierre_ajustado=Decimal("95"),
            ),
            SimpleNamespace(
                fecha=date(2024, 1, 3),
                cierre=Decimal("110"),
                cierre_ajustado=Decimal("105"),
            ),
        ],
    )

    service = HistoricalDataService(
        market_repository=repository,
        source_name="Alpha Vantage",
    )

    asset_id = uuid4()

    result = await service.load_asset_history(
        asset_id=asset_id,
        assigned_percentage=Decimal("100"),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )

    assert result.asset_id == asset_id
    assert result.prices[0].price == Decimal("95")
    assert result.prices[1].price == Decimal("105")


@pytest.mark.asyncio
async def test_load_asset_history_falls_back_to_close(
) -> None:
    source = SimpleNamespace(id=uuid4())

    repository = build_repository(
        source=source,
        prices=[
            SimpleNamespace(
                fecha=date(2024, 1, 2),
                cierre=Decimal("100"),
                cierre_ajustado=None,
            ),
        ],
    )

    service = HistoricalDataService(
        market_repository=repository,
        source_name="Alpha Vantage",
    )

    result = await service.load_asset_history(
        asset_id=uuid4(),
        assigned_percentage=Decimal("100"),
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )

    assert result.prices[0].price == Decimal("100")


@pytest.mark.asyncio
async def test_load_asset_history_rejects_missing_source(
) -> None:
    repository = build_repository(
        source=None,
    )

    service = HistoricalDataService(
        market_repository=repository,
        source_name="Alpha Vantage",
    )

    with pytest.raises(
        SimulationHistoricalSourceUnavailableError
    ):
        await service.load_asset_history(
            asset_id=uuid4(),
            assigned_percentage=Decimal("100"),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

    repository.list_asset_prices_for_simulation.assert_not_awaited()


@pytest.mark.asyncio
async def test_load_asset_history_rejects_missing_prices(
) -> None:
    source = SimpleNamespace(id=uuid4())

    repository = build_repository(
        source=source,
        prices=[],
    )

    service = HistoricalDataService(
        market_repository=repository,
        source_name="Alpha Vantage",
    )

    with pytest.raises(
        SimulationHistoricalPriceNotFoundError
    ):
        await service.load_asset_history(
            asset_id=uuid4(),
            assigned_percentage=Decimal("100"),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )


def test_historical_data_service_rejects_empty_source(
) -> None:
    repository = build_repository(
        source=None
    )

    with pytest.raises(
        ValueError,
        match="fuente histórica",
    ):
        HistoricalDataService(
            market_repository=repository,
            source_name="   ",
        )