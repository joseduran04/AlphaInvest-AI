from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from tests.unit.modules.news.test_mongodb_repository import (
    build_document,
)

from alphainvest.modules.news.infrastructure.storage_coordinator import (
    SqlAlchemyNewsStorageCoordinator,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_storage_coordinator_opens_independent_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()

    context = AsyncMock()
    context.__aenter__.return_value = (
        session
    )

    context.__aexit__.return_value = (
        None
    )

    session_factory = MagicMock(
        return_value=context
    )

    result = SimpleNamespace(
        reference_id=uuid4(),
        mongo_document_id=(
            "6a8c7c674a596c140029999e"
        ),
        mongo_created=True,
    )

    store_mock = AsyncMock(
        return_value=result
    )

    monkeypatch.setattr(
        (
            "alphainvest.modules.news."
            "infrastructure."
            "storage_coordinator."
            "NewsStorageService."
            "store_for_asset"
        ),
        store_mock,
    )

    coordinator = (
        SqlAlchemyNewsStorageCoordinator(
            session_factory=(
                session_factory
            ),
            mongo_repository=(
                MagicMock()
            ),
        )
    )

    response = (
        await coordinator
        .store_for_asset(
            asset_id=uuid4(),
            document=build_document(),
            provider_name=(
                "Alpha Vantage"
            ),
        )
    )

    assert response is result

    session_factory.assert_called_once()
    store_mock.assert_awaited_once()