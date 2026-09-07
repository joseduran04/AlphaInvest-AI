from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from bson import ObjectId
from bson.decimal128 import Decimal128

from alphainvest.modules.news.domain.news_document import (
    NewsDocument,
    NewsTickerSentiment,
    NewsTopic,
)
from alphainvest.modules.news.infrastructure.mongodb_repository import (
    MongoNewsRepository,
)


def build_document() -> NewsDocument:
    return NewsDocument(
        title="Apple headline",
        url="https://example.com/apple",
        published_at=datetime(
            2026,
            8,
            24,
            12,
            0,
            tzinfo=UTC,
        ),
        authors=(
            "Example Author",
        ),
        summary="Example summary",
        banner_image=None,
        source="Example Source",
        category_within_source=(
            "Markets"
        ),
        source_domain="example.com",
        topics=(
            NewsTopic(
                topic="Technology",
                relevance_score=Decimal(
                    "0.8"
                ),
            ),
        ),
        provider_sentiment_score=(
            Decimal("0.2")
        ),
        provider_sentiment_label=(
            "Somewhat-Bullish"
        ),
        ticker_sentiment=(
            NewsTickerSentiment(
                ticker="AAPL",
                relevance_score=Decimal(
                    "0.9"
                ),
                sentiment_score=Decimal(
                    "0.3"
                ),
                sentiment_label=(
                    "Somewhat-Bullish"
                ),
            ),
        ),
        raw_payload={
            "title": "Apple headline",
        },
    )


def build_repository(
) -> tuple[
    MongoNewsRepository,
    MagicMock,
]:
    collection = MagicMock()

    database = MagicMock()
    database.__getitem__.return_value = (
        collection
    )

    client = MagicMock()
    client.__getitem__.return_value = (
        database
    )

    repository = MongoNewsRepository(
        client=client,
        database_name=(
            "alphainvest_documents"
        ),
        collection_name="noticias",
    )

    return repository, collection


@pytest.mark.asyncio
async def test_creates_news_document() -> None:
    repository, collection = (
        build_repository()
    )

    document_id = ObjectId()

    collection.update_one = AsyncMock(
        return_value=SimpleNamespace(
            upserted_id=document_id
        )
    )

    result = await repository.upsert_news(
        document=build_document(),
        provider_name="Alpha Vantage",
    )

    assert (
        result.document_id
        == str(document_id)
    )

    assert result.created is True

    collection.update_one.assert_awaited_once()


@pytest.mark.asyncio
async def test_reuses_existing_news_document(
) -> None:
    repository, collection = (
        build_repository()
    )

    document_id = ObjectId()

    collection.update_one = AsyncMock(
        return_value=SimpleNamespace(
            upserted_id=None
        )
    )

    collection.find_one = AsyncMock(
        return_value={
            "_id": document_id,
        }
    )

    result = await repository.upsert_news(
        document=build_document(),
        provider_name="Alpha Vantage",
    )

    assert (
        result.document_id
        == str(document_id)
    )

    assert result.created is False

    collection.find_one.assert_awaited_once()


def test_builds_stable_deduplication_key(
) -> None:
    first = (
        MongoNewsRepository
        .build_deduplication_key(
            provider_name=(
                "Alpha Vantage"
            ),
            url=(
                "https://example.com/apple"
            ),
        )
    )

    second = (
        MongoNewsRepository
        .build_deduplication_key(
            provider_name=(
                "alpha vantage"
            ),
            url=(
                "https://example.com/apple"
            ),
        )
    )

    assert first == second
    assert len(first) == 64


def test_serializes_decimals_as_decimal128(
) -> None:
    document = build_document()

    serialized = (
        MongoNewsRepository
        ._serialize_document(
            document=document,
            provider_name=(
                "Alpha Vantage"
            ),
            deduplication_key="test",
        )
    )

    topics = serialized["topics"]

    assert isinstance(
        topics,
        list,
    )

    assert isinstance(
        topics[0]["relevance_score"],
        Decimal128,
    )

    provider_sentiment = (
        serialized[
            "provider_sentiment"
        ]
    )

    assert isinstance(
        provider_sentiment["score"],
        Decimal128,
    )


@pytest.mark.asyncio
async def test_creates_required_indexes(
) -> None:
    repository, collection = (
        build_repository()
    )

    collection.create_index = (
        AsyncMock()
    )

    await repository.ensure_indexes()

    assert (
        collection.create_index.await_count
        == 3
    )


@pytest.mark.asyncio
async def test_deletes_news_document(
) -> None:
    repository, collection = (
        build_repository()
    )

    collection.delete_one = AsyncMock(
        return_value=SimpleNamespace(
            deleted_count=1
        )
    )

    document_id = str(
        ObjectId()
    )

    deleted = (
        await repository
        .delete_by_document_id(
            document_id
        )
    )

    assert deleted is True

    collection.delete_one.assert_awaited_once()