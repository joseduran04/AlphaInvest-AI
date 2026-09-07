from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from tests.unit.modules.news.test_mongodb_repository import (
    build_document,
)

from alphainvest.modules.news.application.storage_service import (
    NewsStorageService,
)
from alphainvest.modules.news.domain.exceptions import (
    NewsPersistenceError,
)
from alphainvest.modules.news.domain.news_persistence import (
    NewsPersistenceResult,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_stores_news_in_both_datastores(
) -> None:
    asset_id = uuid4()
    reference_id = uuid4()

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                simbolo="AAPL"
            )
        ),
        upsert_news_reference=AsyncMock(
            return_value=reference_id
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    mongo_repository = SimpleNamespace(
        upsert_news=AsyncMock(
            return_value=(
                NewsPersistenceResult(
                    document_id=(
                        "6a8c7c674a596c140029999e"
                    ),
                    created=True,
                    deduplication_key=(
                        "test-key"
                    ),
                )
            )
        ),
        delete_by_document_id=AsyncMock(),
    )

    service = NewsStorageService(
        market_repository=(
            market_repository
        ),
        mongo_repository=(
            mongo_repository
        ),
    )

    result = await service.store_for_asset(
        asset_id=asset_id,
        document=build_document(),
        provider_name="Alpha Vantage",
    )

    assert result.reference_id == reference_id

    assert (
        result.mongo_document_id
        == "6a8c7c674a596c140029999e"
    )

    assert result.mongo_created is True

    market_repository.commit.assert_awaited_once()

    market_repository.rollback.assert_not_awaited()

    market_repository.upsert_news_reference.assert_awaited_once()

    call = (
        market_repository
        .upsert_news_reference
        .await_args
    )

    assert (
        call.kwargs["relevance"]
        == Decimal("0.9")
    )


@pytest.mark.asyncio
async def test_compensates_new_mongo_document_when_postgres_fails(
) -> None:
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                simbolo="AAPL"
            )
        ),
        upsert_news_reference=AsyncMock(
            side_effect=RuntimeError(
                "postgres failure"
            )
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    mongo_repository = SimpleNamespace(
        upsert_news=AsyncMock(
            return_value=(
                NewsPersistenceResult(
                    document_id=(
                        "6a8c7c674a596c140029999e"
                    ),
                    created=True,
                    deduplication_key=(
                        "test-key"
                    ),
                )
            )
        ),
        delete_by_document_id=AsyncMock(
            return_value=True
        ),
    )

    service = NewsStorageService(
        market_repository=(
            market_repository
        ),
        mongo_repository=(
            mongo_repository
        ),
    )

    with pytest.raises(
        NewsPersistenceError
    ):
        await service.store_for_asset(
            asset_id=uuid4(),
            document=build_document(),
            provider_name="Alpha Vantage",
        )

    market_repository.rollback.assert_awaited_once()

    mongo_repository.delete_by_document_id.assert_awaited_once_with(
        "6a8c7c674a596c140029999e"
    )


@pytest.mark.asyncio
async def test_does_not_delete_existing_mongo_document_when_postgres_fails(
) -> None:
    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=SimpleNamespace(
                simbolo="AAPL"
            )
        ),
        upsert_news_reference=AsyncMock(
            side_effect=RuntimeError(
                "postgres failure"
            )
        ),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    mongo_repository = SimpleNamespace(
        upsert_news=AsyncMock(
            return_value=(
                NewsPersistenceResult(
                    document_id=(
                        "6a8c7c674a596c140029999e"
                    ),
                    created=False,
                    deduplication_key=(
                        "test-key"
                    ),
                )
            )
        ),
        delete_by_document_id=AsyncMock(),
    )

    service = NewsStorageService(
        market_repository=(
            market_repository
        ),
        mongo_repository=(
            mongo_repository
        ),
    )

    with pytest.raises(
        NewsPersistenceError
    ):
        await service.store_for_asset(
            asset_id=uuid4(),
            document=build_document(),
            provider_name="Alpha Vantage",
        )

    mongo_repository.delete_by_document_id.assert_not_awaited()