from types import SimpleNamespace

import pytest
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

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