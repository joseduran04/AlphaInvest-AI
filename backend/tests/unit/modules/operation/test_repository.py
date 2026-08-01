from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_acquire_process_lock_returns_true() -> None:
    result = SimpleNamespace(
        scalar_one=lambda: True
    )
    session = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )
    repository = OperationRepository(session)

    acquired = await repository.acquire_process_lock(
        process_type="CARGA_MERCADO",
        lock_key="MARKET_PRICE_SYNC:asset-id",
        owner="alphainvest-api",
        process_id="process-id",
        duration_seconds=120,
        entity_type="ACTIVO",
        entity_id="asset-id",
        metadata={"symbol": "AAPL"},
    )

    assert acquired is True
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_release_process_lock_returns_true() -> None:
    result = SimpleNamespace(
        scalar_one=lambda: True
    )
    session = SimpleNamespace(
        execute=AsyncMock(return_value=result)
    )
    repository = OperationRepository(session)

    released = await repository.release_process_lock(
        lock_key="MARKET_PRICE_SYNC:asset-id",
        process_id="process-id",
    )

    assert released is True
    session.execute.assert_awaited_once()