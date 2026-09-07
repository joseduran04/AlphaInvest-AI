from types import SimpleNamespace
from unittest.mock import (
    AsyncMock,
    MagicMock,
    patch,
)
from uuid import uuid4

import pytest

from alphainvest.core.config import Settings
from alphainvest.worker.jobs.news import (
    NEWS_WORKER_LIMIT,
    synchronize_configured_news,
)
from alphainvest.worker.registry import (
    WORKER_JOB_REGISTRY,
)

pytestmark = pytest.mark.unit


def test_news_job_is_registered() -> None:
    assert (
        "SINCRONIZAR_NOTICIAS"
        in WORKER_JOB_REGISTRY
    )


def test_news_worker_limit() -> None:
    assert NEWS_WORKER_LIMIT == 20


@pytest.mark.asyncio
async def test_news_worker_without_symbols_does_nothing(
) -> None:
    settings = MagicMock(
        spec=Settings
    )

    settings.worker_price_symbols = []

    with patch(
        
            "alphainvest.worker.jobs.news."
            "create_mongo_client"
        
    ) as create_mongo_client:
        await synchronize_configured_news(
            settings
        )

    create_mongo_client.assert_not_called()


@pytest.mark.asyncio
async def test_news_worker_synchronizes_configured_asset(
) -> None:
    settings = MagicMock(
        spec=Settings
    )

    settings.worker_price_symbols = [
        "AAPL"
    ]

    settings.mongodb_database = (
        "alphainvest_documents"
    )

    settings.mongodb_news_collection = (
        "noticias"
    )

    asset = SimpleNamespace(
        id=uuid4(),
        simbolo="AAPL",
    )

    result = SimpleNamespace(
        symbol="AAPL",
        execution_id=uuid4(),
        received=5,
        created=3,
        reused=2,
        failed=0,
    )

    market_repository = SimpleNamespace(
        get_active_asset_by_symbol=(
            AsyncMock(
                return_value=asset
            )
        )
    )

    operation_repository = (
        MagicMock()
    )

    mongo_repository = SimpleNamespace(
        ensure_indexes=AsyncMock()
    )

    mongo_client = MagicMock()
    mongo_client.close = AsyncMock()

    service = SimpleNamespace(
        synchronize_asset=AsyncMock(
            return_value=result
        )
    )

    session = MagicMock()

    session_context = AsyncMock()

    session_context.__aenter__.return_value = (
        session
    )

    session_context.__aexit__.return_value = (
        None
    )

    with (
        patch(
            (
                "alphainvest.worker.jobs.news."
                "create_mongo_client"
            ),
            return_value=mongo_client,
        ),
        patch(
            (
                "alphainvest.worker.jobs.news."
                "MongoNewsRepository"
            ),
            return_value=(
                mongo_repository
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs.news."
                "SqlAlchemyNewsStorageCoordinator"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs.news."
                "create_alpha_vantage_news_provider"
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs.news."
                "AsyncSessionFactory"
            ),
            return_value=session_context,
        ),
        patch(
            (
                "alphainvest.worker.jobs.news."
                "MarketRepository"
            ),
            return_value=(
                market_repository
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs.news."
                "OperationRepository"
            ),
            return_value=(
                operation_repository
            ),
        ),
        patch(
            (
                "alphainvest.worker.jobs.news."
                "NewsSynchronizationService"
            ),
            return_value=service,
        ),
    ):
        await synchronize_configured_news(
            settings
        )

    (
        market_repository
        .get_active_asset_by_symbol
        .assert_awaited_once_with(
            "AAPL"
        )
    )

    service.synchronize_asset.assert_awaited_once()

    call = (
        service
        .synchronize_asset
        .await_args
    )

    assert (
        call.kwargs["asset_id"]
        == asset.id
    )

    assert (
        call.kwargs["requested_by"]
        is None
    )

    assert (
        call.kwargs["limit"]
        == NEWS_WORKER_LIMIT
    )

    mongo_repository.ensure_indexes.assert_awaited_once()

    mongo_client.close.assert_awaited_once()