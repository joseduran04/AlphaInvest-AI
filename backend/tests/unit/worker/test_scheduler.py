from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from alphainvest.core.config import Settings
from alphainvest.worker.scheduler import (
    AlphaInvestScheduler,
)

pytestmark = pytest.mark.unit


def test_builds_cron_trigger() -> None:
    job = SimpleNamespace(
        codigo="ACTUALIZAR_PRECIOS_DIARIOS",
        tipo="CRON",
        expresion_cron="0 23 * * 1-5",
        intervalo_segundos=None,
        zona_horaria="America/Mexico_City",
    )

    trigger = AlphaInvestScheduler._build_trigger(job)

    assert isinstance(trigger, CronTrigger)


def test_builds_interval_trigger() -> None:
    job = SimpleNamespace(
        codigo="DEPURAR_CONTROL_PROCESOS",
        tipo="INTERVALO",
        expresion_cron=None,
        intervalo_segundos=300,
        zona_horaria="UTC",
    )

    trigger = AlphaInvestScheduler._build_trigger(job)

    assert isinstance(trigger, IntervalTrigger)


def test_rejects_cron_without_expression() -> None:
    job = SimpleNamespace(
        codigo="INVALID_JOB",
        tipo="CRON",
        expresion_cron=None,
        intervalo_segundos=None,
        zona_horaria="UTC",
    )

    with pytest.raises(
        ValueError,
        match="no tiene CRON",
    ):
        AlphaInvestScheduler._build_trigger(job)


def test_builds_simulation_interval_trigger() -> None:
    job = SimpleNamespace(
        codigo="PROCESAR_SIMULACIONES_PENDIENTES",
        tipo="INTERVALO",
        expresion_cron=None,
        intervalo_segundos=60,
        zona_horaria="America/Mexico_City",
    )

    trigger = AlphaInvestScheduler._build_trigger(
        job
    )

    assert isinstance(
        trigger,
        IntervalTrigger,
    )


@pytest.mark.asyncio
async def test_executes_job_without_retry() -> None:
    settings = Settings()

    scheduler = AlphaInvestScheduler(
        settings
    )

    worker_job = AsyncMock()

    await scheduler._execute_with_retries(
        job_code="TEST_JOB",
        worker_job=worker_job,
        max_retries=3,
    )

    assert worker_job.await_count == 1


@pytest.mark.asyncio
async def test_retries_failed_job() -> None:
    settings = Settings()

    scheduler = AlphaInvestScheduler(
        settings
    )

    worker_job = AsyncMock(
        side_effect=[
            RuntimeError("fallo 1"),
            RuntimeError("fallo 2"),
            None,
        ]
    )

    await scheduler._execute_with_retries(
        job_code="TEST_JOB",
        worker_job=worker_job,
        max_retries=3,
    )

    assert worker_job.await_count == 3


@pytest.mark.asyncio
async def test_exhausts_job_retries() -> None:
    settings = Settings()

    scheduler = AlphaInvestScheduler(
        settings
    )

    worker_job = AsyncMock(
        side_effect=RuntimeError(
            "fallo permanente"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="fallo permanente",
    ):
        await scheduler._execute_with_retries(
            job_code="TEST_JOB",
            worker_job=worker_job,
            max_retries=3,
        )

    assert worker_job.await_count == 4


@pytest.mark.asyncio
async def test_run_job_now_executes_retry_pipeline_once(
) -> None:
    settings = Settings()

    scheduler = AlphaInvestScheduler(
        settings
    )

    worker_job = AsyncMock()

    job = SimpleNamespace(
        codigo="TEST_JOB",
        maximo_reintentos=3,
    )

    repository = SimpleNamespace(
        get_job_by_code=AsyncMock(
            return_value=job
        )
    )

    session = AsyncMock()

    context = AsyncMock()
    context.__aenter__.return_value = session
    context.__aexit__.return_value = None

    execute_with_retries = AsyncMock()

    with (
        patch.dict(
            "alphainvest.worker.scheduler."
            "WORKER_JOB_REGISTRY",
            {
                "TEST_JOB": worker_job,
            },
            clear=False,
        ),
        patch(
            "alphainvest.worker.scheduler."
            "AsyncSessionFactory",
            return_value=context,
        ),
        patch(
            "alphainvest.worker.scheduler."
            "OperationRepository",
            return_value=repository,
        ),
        patch.object(
            scheduler,
            "_execute_with_retries",
            execute_with_retries,
        ),
    ):
        await scheduler.run_job_now(
            "TEST_JOB"
        )

    execute_with_retries.assert_awaited_once_with(
        job_code="TEST_JOB",
        worker_job=worker_job,
        max_retries=3,
    )

    worker_job.assert_not_awaited()


def test_builds_news_interval_trigger(
) -> None:
    job = SimpleNamespace(
        codigo="SINCRONIZAR_NOTICIAS",
        tipo="INTERVALO",
        expresion_cron=None,
        intervalo_segundos=1800,
        zona_horaria=(
            "America/Mexico_City"
        ),
    )

    trigger = (
        AlphaInvestScheduler
        ._build_trigger(
            job
        )
    )

    assert isinstance(
        trigger,
        IntervalTrigger,
    )