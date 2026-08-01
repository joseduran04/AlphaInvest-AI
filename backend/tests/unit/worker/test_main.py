from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from alphainvest.worker.main import run_worker

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_disabled_worker_does_not_create_scheduler() -> None:
    settings = SimpleNamespace(
        worker_enabled=False,
    )

    with (
        patch(
            "alphainvest.worker.main.get_settings",
            return_value=settings,
        ),
        patch(
            "alphainvest.worker.main.AlphaInvestScheduler",
        ) as scheduler_class,
    ):
        await run_worker()

    scheduler_class.assert_not_called()


@pytest.mark.asyncio
async def test_run_once_executes_job_and_finishes() -> None:
    settings = SimpleNamespace(
        worker_enabled=True,
        worker_run_once=True,
        worker_run_on_startup=False,
    )

    scheduler = SimpleNamespace(
        run_price_sync_now=AsyncMock(),
        shutdown=Mock(),
    )

    with (
        patch(
            "alphainvest.worker.main.get_settings",
            return_value=settings,
        ),
        patch(
            "alphainvest.worker.main.AlphaInvestScheduler",
            return_value=scheduler,
        ),
        patch(
            "alphainvest.worker.main.dispose_engine",
            new=AsyncMock(),
        ) as dispose_engine,
    ):
        await run_worker()

    scheduler.run_price_sync_now.assert_awaited_once()
    scheduler.shutdown.assert_called_once()
    dispose_engine.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_once_does_not_load_cron_jobs() -> None:
    settings = SimpleNamespace(
        worker_enabled=True,
        worker_run_once=True,
        worker_run_on_startup=False,
    )

    scheduler = SimpleNamespace(
        run_price_sync_now=AsyncMock(),
        load_jobs=AsyncMock(),
        start=Mock(),
        shutdown=Mock(),
    )

    with (
        patch(
            "alphainvest.worker.main.get_settings",
            return_value=settings,
        ),
        patch(
            "alphainvest.worker.main.AlphaInvestScheduler",
            return_value=scheduler,
        ),
        patch(
            "alphainvest.worker.main.dispose_engine",
            new=AsyncMock(),
        ),
    ):
        await run_worker()

    scheduler.run_price_sync_now.assert_awaited_once()
    scheduler.load_jobs.assert_not_awaited()
    scheduler.start.assert_not_called()