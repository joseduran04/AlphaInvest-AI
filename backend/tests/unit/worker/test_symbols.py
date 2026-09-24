from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from alphainvest.core.config import Settings
from alphainvest.worker.jobs.symbols import (
    merge_symbols,
    resolve_worker_symbols,
)

pytestmark = pytest.mark.unit


def test_merge_symbols_keeps_order_and_removes_duplicates() -> None:
    assert merge_symbols(
        ["AAPL", "meta "],
        ["AMZN", "META", "AAPL"],
    ) == ["AAPL", "META", "AMZN"]


def build_settings(*, in_use: bool, all_active: bool = False) -> MagicMock:
    settings = MagicMock(spec=Settings)
    settings.worker_price_symbols = ["AAPL"]
    settings.worker_price_sync_assets_in_use = in_use
    settings.worker_sync_all_active_assets = all_active
    return settings


def build_session_factory(symbols_in_use: list[str]) -> MagicMock:
    session_context = AsyncMock()
    session_context.__aenter__.return_value = MagicMock()
    factory = MagicMock(return_value=session_context)
    return factory


@pytest.mark.asyncio
async def test_resolve_symbols_only_configured_when_disabled() -> None:
    assert await resolve_worker_symbols(
        build_settings(in_use=False)
    ) == ["AAPL"]


@pytest.mark.asyncio
async def test_resolve_symbols_adds_assets_in_use() -> None:
    """Caso META/AMZN: activos usados deben sincronizarse sin tocar el .env."""

    repository = MagicMock()
    repository.list_symbols_in_use = AsyncMock(
        return_value=["AMZN", "META"]
    )

    with (
        patch(
            "alphainvest.worker.jobs.symbols.AsyncSessionFactory",
            build_session_factory([]),
        ),
        patch(
            "alphainvest.worker.jobs.symbols.MarketRepository",
            return_value=repository,
        ),
    ):
        symbols = await resolve_worker_symbols(
            build_settings(in_use=True)
        )

    assert symbols == ["AAPL", "AMZN", "META"]


@pytest.mark.asyncio
async def test_resolve_symbols_falls_back_to_configured_on_error() -> None:
    repository = MagicMock()
    repository.list_symbols_in_use = AsyncMock(
        side_effect=RuntimeError("sin conexión")
    )

    with (
        patch(
            "alphainvest.worker.jobs.symbols.AsyncSessionFactory",
            build_session_factory([]),
        ),
        patch(
            "alphainvest.worker.jobs.symbols.MarketRepository",
            return_value=repository,
        ),
    ):
        symbols = await resolve_worker_symbols(
            build_settings(in_use=True)
        )

    assert symbols == ["AAPL"]


@pytest.mark.asyncio
async def test_resolve_symbols_uses_whole_catalog_when_enabled() -> None:
    repository = MagicMock()
    repository.list_active_symbols = AsyncMock(
        return_value=["AAPL", "AMXL", "NVDA"]
    )
    repository.list_symbols_in_use = AsyncMock(return_value=["META"])

    with (
        patch(
            "alphainvest.worker.jobs.symbols.AsyncSessionFactory",
            build_session_factory([]),
        ),
        patch(
            "alphainvest.worker.jobs.symbols.MarketRepository",
            return_value=repository,
        ),
    ):
        symbols = await resolve_worker_symbols(
            build_settings(in_use=True, all_active=True)
        )

    assert symbols == ["AAPL", "AMXL", "NVDA"]
    repository.list_symbols_in_use.assert_not_awaited()
