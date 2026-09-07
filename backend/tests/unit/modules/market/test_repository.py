from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_list_asset_prices_for_simulation(
) -> None:
    session = MagicMock()
    session.execute = AsyncMock()

    first_price = SimpleNamespace(
        fecha=date(2024, 1, 2)
    )
    second_price = SimpleNamespace(
        fecha=date(2024, 1, 3)
    )

    result = MagicMock()
    result.scalars.return_value.all.return_value = [
        first_price,
        second_price,
    ]
    session.execute.return_value = result

    repository = MarketRepository(session)

    prices = (
        await repository
        .list_asset_prices_for_simulation(
            asset_id=uuid4(),
            source_id=uuid4(),
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )
    )

    assert prices == [
        first_price,
        second_price,
    ]
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_upsert_news_reference(
) -> None:
    session = MagicMock()
    session.execute = AsyncMock()

    reference_id = uuid4()

    result = MagicMock()
    result.scalar_one.return_value = (
        reference_id
    )

    session.execute.return_value = result

    repository = MarketRepository(
        session
    )

    stored_id = (
        await repository
        .upsert_news_reference(
            asset_id=uuid4(),
            mongo_document_id=(
                "6a8c7c674a596c140029999e"
            ),
            title="Apple headline",
            source="Example Source",
            url=(
                "https://example.com/apple"
            ),
            published_at=datetime(
                2026,
                8,
                24,
                12,
                0,
                tzinfo=UTC,
            ),
            language=None,
            relevance=Decimal(
                "0.9"
            ),
        )
    )

    assert stored_id == reference_id
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_news_references(
) -> None:
    session = MagicMock()
    session.execute = AsyncMock()

    reference = SimpleNamespace(
        id=uuid4()
    )

    rows_result = MagicMock()

    rows_result.scalars.return_value.all.return_value = [
        reference
    ]

    count_result = MagicMock()

    count_result.scalar_one.return_value = 1

    session.execute.side_effect = [
        rows_result,
        count_result,
    ]

    repository = MarketRepository(
        session
    )

    rows, total = (
        await repository
        .list_news_references(
            asset_id=uuid4(),
            start_at=None,
            end_at=None,
            limit=20,
            offset=0,
        )
    )

    assert rows == [reference]
    assert total == 1

    assert session.execute.await_count == 2