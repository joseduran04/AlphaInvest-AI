from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from tests.unit.modules.news.test_mongodb_repository import (
    build_document,
)

from alphainvest.modules.news.application.synchronization_service import (
    NEWS_SYNC_JOB_CODE,
    NewsSynchronizationService,
)
from alphainvest.modules.news.domain.news_storage import (
    NewsStorageResult,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_synchronizes_asset_news(
) -> None:
    asset_id = uuid4()
    execution_id = uuid4()

    asset = SimpleNamespace(
        id=asset_id,
        simbolo="AAPL",
    )

    source = SimpleNamespace(
        id=uuid4(),
        nombre="Alpha Vantage",
    )

    job = SimpleNamespace(
        id=uuid4(),
        codigo=NEWS_SYNC_JOB_CODE,
        tiempo_maximo_segundos=1200,
    )

    execution = SimpleNamespace(
        id=execution_id
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        ),
        get_financial_source_by_name=(
            AsyncMock(
                return_value=source
            )
        ),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(
            return_value=job
        ),
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        create_execution=AsyncMock(
            return_value=execution
        ),
        mark_completed=AsyncMock(),
        update_job_last_execution=AsyncMock(),
        release_process_lock=AsyncMock(
            return_value=True
        ),
        get_execution=AsyncMock(),
        mark_failed=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    provider = SimpleNamespace(
        source_name="Alpha Vantage",
        fetch_news=AsyncMock(
            return_value=[
                build_document(),
                build_document(),
            ]
        ),
    )

    storage = SimpleNamespace(
        store_for_asset=AsyncMock(
            side_effect=[
                NewsStorageResult(
                    reference_id=uuid4(),
                    mongo_document_id=(
                        "6a8c7c674a596c140029999e"
                    ),
                    mongo_created=True,
                ),
                NewsStorageResult(
                    reference_id=uuid4(),
                    mongo_document_id=(
                        "6a8c7c674a596c140029999e"
                    ),
                    mongo_created=False,
                ),
            ]
        )
    )

    service = NewsSynchronizationService(
        market_repository=(
            market_repository
        ),
        operation_repository=(
            operation_repository
        ),
        provider=provider,
        storage=storage,
    )

    result = await service.synchronize_asset(
        asset_id=asset_id,
        requested_by=uuid4(),
        start_at=None,
        end_at=None,
        limit=20,
    )

    assert result.received == 2
    assert result.created == 1
    assert result.reused == 1
    assert result.failed == 0

    operation_repository.get_job_by_code.assert_awaited_once_with(
        NEWS_SYNC_JOB_CODE
    )

    operation_repository.mark_completed.assert_awaited_once()

    operation_repository.release_process_lock.assert_awaited_once()

    assert (
        operation_repository.commit.await_count
        == 2
    )


@pytest.mark.asyncio
async def test_counts_article_persistence_failure(
) -> None:
    asset = SimpleNamespace(
        id=uuid4(),
        simbolo="AAPL",
    )

    source = SimpleNamespace(
        id=uuid4(),
        nombre="Alpha Vantage",
    )

    job = SimpleNamespace(
        id=uuid4(),
        tiempo_maximo_segundos=1200,
    )

    execution = SimpleNamespace(
        id=uuid4()
    )

    market_repository = SimpleNamespace(
        get_asset=AsyncMock(
            return_value=asset
        ),
        get_financial_source_by_name=(
            AsyncMock(
                return_value=source
            )
        ),
    )

    operation_repository = SimpleNamespace(
        get_job_by_code=AsyncMock(
            return_value=job
        ),
        acquire_process_lock=AsyncMock(
            return_value=True
        ),
        create_execution=AsyncMock(
            return_value=execution
        ),
        mark_completed=AsyncMock(),
        update_job_last_execution=AsyncMock(),
        release_process_lock=AsyncMock(
            return_value=True
        ),
        get_execution=AsyncMock(),
        mark_failed=AsyncMock(),
        commit=AsyncMock(),
        rollback=AsyncMock(),
    )

    provider = SimpleNamespace(
        source_name="Alpha Vantage",
        fetch_news=AsyncMock(
            return_value=[
                build_document()
            ]
        ),
    )

    from alphainvest.modules.news.domain.exceptions import (
        NewsPersistenceError,
    )

    storage = SimpleNamespace(
        store_for_asset=AsyncMock(
            side_effect=(
                NewsPersistenceError(
                    "storage failure"
                )
            )
        )
    )

    service = NewsSynchronizationService(
        market_repository=(
            market_repository
        ),
        operation_repository=(
            operation_repository
        ),
        provider=provider,
        storage=storage,
    )

    result = await service.synchronize_asset(
        asset_id=asset.id,
        requested_by=None,
        start_at=None,
        end_at=None,
        limit=20,
    )

    assert result.received == 1
    assert result.created == 0
    assert result.reused == 0
    assert result.failed == 1