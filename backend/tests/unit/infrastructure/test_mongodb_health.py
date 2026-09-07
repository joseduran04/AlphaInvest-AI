from unittest.mock import AsyncMock, MagicMock

import pytest

from alphainvest.infrastructure.mongodb.health import (
    check_mongodb,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_mongodb_health_up() -> None:
    client = MagicMock()

    client.admin.command = AsyncMock(
        return_value={"ok": 1}
    )

    result = await check_mongodb(
        client
    )

    assert result.status == "up"
    assert result.latency_ms is not None
    assert result.error is None

    client.admin.command.assert_awaited_once_with(
        {"ping": 1}
    )


@pytest.mark.asyncio
async def test_mongodb_health_down() -> None:
    client = MagicMock()

    client.admin.command = AsyncMock(
        side_effect=RuntimeError(
            "mongo unavailable"
        )
    )

    result = await check_mongodb(
        client
    )

    assert result.status == "down"
    assert result.latency_ms is None
    assert result.error == "RuntimeError"