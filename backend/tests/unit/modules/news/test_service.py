from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from bson import ObjectId
from bson.decimal128 import Decimal128

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
)
from alphainvest.modules.news.application.service import (
    NewsService,
)
from alphainvest.modules.news.domain.exceptions import (
    InvalidNewsDateRangeError,
    NewsDocumentNotFoundError,
)

pytestmark = pytest.mark.unit


def build_reference() -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        activo_id=uuid4(),
        mongo_document_id=str(
            ObjectId()
        ),
        titulo="Apple headline",
        fuente="Example Source",
        url="https://example.com/apple",
        fecha_publicacion=datetime(
            2026,
            8,
            24,
            12,
            0,
            tzinfo=UTC,
        ),
        idioma=None,
        relevancia=Decimal(
            "0.90000000"
        ),
    )


def build_mongo_document(
) -> dict[str, object]:
    return {
        "authors": [
            "Example Author"
        ],
        "summary": "Example summary",
        "banner_image": None,
        "category_within_source": (
            "Markets"
        ),
        "source_domain": (
            "example.com"
        ),
        "topics": [
            {
                "topic": "Technology",
                "relevance_score": (
                    Decimal128("0.8")
                ),
            }
        ],
        "provider_sentiment": {
            "score": Decimal128(
                "0.2"
            ),
            "label": (
                "Somewhat-Bullish"
            ),
        },
        "ticker_sentiment": [
            {
                "ticker": "AAPL",
                "relevance_score": (
                    Decimal128("0.9")
                ),
                "sentiment_score": (
                    Decimal128("0.3")
                ),
                "sentiment_label": (
                    "Somewhat-Bullish"
                ),
            }
        ],
    }


@pytest.mark.asyncio
async def test_lists_asset_news() -> None:
    reference = build_reference()

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=reference.activo_id
            )
        ),
        list_news_references=AsyncMock(
            return_value=(
                [reference],
                1,
            )
        ),
    )

    mongo_repository = SimpleNamespace(
        get_by_document_id=AsyncMock(
            return_value=(
                build_mongo_document()
            )
        )
    )

    service = NewsService(
        market_repository=(
            market_repository
        ),
        mongo_repository=(
            mongo_repository
        ),
    )

    result = await service.list_asset_news(
        asset_id=reference.activo_id,
        start_at=None,
        end_at=None,
        limit=20,
        offset=0,
    )

    assert result.total == 1
    assert len(result.items) == 1

    item = result.items[0]

    assert (
        item.reference_id
        == reference.id
    )

    assert (
        item.summary
        == "Example summary"
    )

    assert (
        item.relevance
        == Decimal("0.90000000")
    )

    assert (
        item.provider_sentiment.score
        == Decimal("0.2")
    )

    assert (
        item.ticker_sentiment[0]
        .ticker
        == "AAPL"
    )


@pytest.mark.asyncio
async def test_rejects_missing_asset(
) -> None:
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=None
        ),
        list_news_references=AsyncMock(),
    )

    mongo_repository = SimpleNamespace(
        get_by_document_id=AsyncMock()
    )

    service = NewsService(
        market_repository=(
            market_repository
        ),
        mongo_repository=(
            mongo_repository
        ),
    )

    with pytest.raises(
        AssetNotFoundError
    ):
        await service.list_asset_news(
            asset_id=uuid4(),
            start_at=None,
            end_at=None,
            limit=20,
            offset=0,
        )

    market_repository.list_news_references.assert_not_awaited()


@pytest.mark.asyncio
async def test_rejects_missing_mongo_document(
) -> None:
    reference = build_reference()

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                id=reference.activo_id
            )
        ),
        list_news_references=AsyncMock(
            return_value=(
                [reference],
                1,
            )
        ),
    )

    mongo_repository = SimpleNamespace(
        get_by_document_id=AsyncMock(
            return_value=None
        )
    )

    service = NewsService(
        market_repository=(
            market_repository
        ),
        mongo_repository=(
            mongo_repository
        ),
    )

    with pytest.raises(
        NewsDocumentNotFoundError
    ):
        await service.list_asset_news(
            asset_id=reference.activo_id,
            start_at=None,
            end_at=None,
            limit=20,
            offset=0,
        )


@pytest.mark.asyncio
async def test_rejects_invalid_date_range(
) -> None:
    service = NewsService(
        market_repository=(
            SimpleNamespace()
        ),
        mongo_repository=(
            SimpleNamespace()
        ),
    )

    with pytest.raises(
        InvalidNewsDateRangeError
    ):
        await service.list_asset_news(
            asset_id=uuid4(),
            start_at=datetime(
                2026,
                8,
                25,
                tzinfo=UTC,
            ),
            end_at=datetime(
                2026,
                8,
                24,
                tzinfo=UTC,
            ),
            limit=20,
            offset=0,
        )