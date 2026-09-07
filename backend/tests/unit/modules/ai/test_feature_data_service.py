from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.domain.exceptions import (
    AIFeatureDataUnavailableError,
)

pytestmark = pytest.mark.unit


def build_prices(
    *,
    asset_id: UUID,
    count: int,
) -> list[SimpleNamespace]:
    start = date(2026, 1, 1)

    return [
        SimpleNamespace(
            activo_id=asset_id,
            fecha=start + timedelta(days=index),
            cierre=Decimal(100 + index),
            cierre_ajustado=Decimal(100 + index),
            volumen=Decimal(1000 + index),
        )
        for index in range(count)
    ]


@pytest.mark.asyncio
async def test_builds_feature_dataset_from_prices() -> None:
    asset_id = uuid4()
    source_id = uuid4()

    repository = SimpleNamespace(
        get_financial_source_by_name=AsyncMock(
            return_value=SimpleNamespace(
                id=source_id,
                activa=True,
            )
        ),
        list_asset_prices_for_simulation=AsyncMock(
            return_value=build_prices(
                asset_id=asset_id,
                count=80,
            )
        ),
    )

    service = AIFeatureDataService(
        market_repository=repository,
        source_name="Yahoo Finance",
    )

    dataset = await service.build_dataset(
        asset_id=asset_id,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 4, 30),
    )

    assert dataset.asset_id == asset_id
    assert dataset.source_id == source_id

    assert dataset.size > 35

    assert dataset.rows[0].sma_20 > 0
    assert dataset.rows[0].ema_20 > 0

    assert (
        dataset.rows[0].date
        > date(2026, 1, 1)
    )


@pytest.mark.asyncio
async def test_uses_adjusted_close() -> None:
    asset_id = uuid4()

    prices = build_prices(
        asset_id=asset_id,
        count=80,
    )

    for price in prices:
        price.cierre = Decimal("200")

    repository = SimpleNamespace(
        get_financial_source_by_name=AsyncMock(
            return_value=SimpleNamespace(
                id=uuid4(),
                activa=True,
            )
        ),
        list_asset_prices_for_simulation=AsyncMock(
            return_value=prices
        ),
    )

    service = AIFeatureDataService(
        market_repository=repository,
        source_name="Yahoo Finance",
    )

    dataset = await service.build_dataset(
        asset_id=asset_id,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 4, 30),
    )

    assert (
        dataset.rows[0].close
        != Decimal("200")
    )


@pytest.mark.asyncio
async def test_rejects_insufficient_history() -> None:
    asset_id = uuid4()

    repository = SimpleNamespace(
        get_financial_source_by_name=AsyncMock(
            return_value=SimpleNamespace(
                id=uuid4(),
                activa=True,
            )
        ),
        list_asset_prices_for_simulation=AsyncMock(
            return_value=build_prices(
                asset_id=asset_id,
                count=20,
            )
        ),
    )

    service = AIFeatureDataService(
        market_repository=repository,
        source_name="Yahoo Finance",
    )

    with pytest.raises(
        AIFeatureDataUnavailableError
    ):
        await service.build_dataset(
            asset_id=asset_id,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 2, 28),
        )


@pytest.mark.asyncio
async def test_rejects_missing_source() -> None:
    repository = SimpleNamespace(
        get_financial_source_by_name=AsyncMock(
            return_value=None
        ),
    )

    service = AIFeatureDataService(
        market_repository=repository,
        source_name="Yahoo Finance",
    )

    with pytest.raises(
        AIFeatureDataUnavailableError
    ):
        await service.build_dataset(
            asset_id=uuid4(),
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )