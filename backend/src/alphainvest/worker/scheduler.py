import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import (  # type: ignore[import-untyped]
    AsyncIOScheduler,
)
from apscheduler.triggers.cron import (  # type: ignore[import-untyped]
    CronTrigger,
)
from apscheduler.triggers.interval import (  # type: ignore[import-untyped]
    IntervalTrigger,
)

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)
from alphainvest.modules.operation.infrastructure.models import (
    ScheduledJobModel,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)
from alphainvest.worker.registry import (
    WORKER_JOB_REGISTRY,
)

logger = logging.getLogger(__name__)


class AlphaInvestScheduler:
    """Carga en APScheduler los trabajos definidos en PostgreSQL."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._scheduler = AsyncIOScheduler(
            timezone=settings.worker_timezone
        )

    async def load_jobs(self) -> int:
        async with AsyncSessionFactory() as session:
            repository = OperationRepository(session)
            jobs = await repository.list_active_scheduled_jobs()

            registered = 0

            for job in jobs:
                worker_job = WORKER_JOB_REGISTRY.get(
                    job.codigo
                )

                if worker_job is None:
                    logger.info(
                        "Trabajo sin implementación: %s",
                        job.codigo,
                    )
                    continue

                trigger = self._build_trigger(job)

                self._scheduler.add_job(
                    worker_job,
                    trigger=trigger,
                    id=job.codigo,
                    name=job.nombre,
                    kwargs={"settings": self._settings},
                    replace_existing=True,
                    max_instances=(
                        self._settings.worker_max_instances
                    ),
                    coalesce=True,
                    misfire_grace_time=(
                        self._settings
                        .worker_misfire_grace_seconds
                    ),
                )

                trigger_timezone = ZoneInfo(
                    job.zona_horaria
                )

                next_execution = trigger.get_next_fire_time(
                    previous_fire_time=None,
                    now=datetime.now(trigger_timezone),
                )

                await repository.update_job_next_execution(
                    job,
                    next_execution,
                )

                registered += 1

            await repository.commit()

            return registered

    def start(self) -> None:
        self._scheduler.start()

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    async def run_price_sync_now(self) -> None:
        worker_job = WORKER_JOB_REGISTRY[
            "ACTUALIZAR_PRECIOS_DIARIOS"
        ]
        await worker_job(self._settings)

    @staticmethod
    def _build_trigger(
        job: ScheduledJobModel,
    ) -> CronTrigger | IntervalTrigger:
        timezone = ZoneInfo(job.zona_horaria)

        if job.tipo == "CRON":
            if not job.expresion_cron:
                raise ValueError(
                    f"El trabajo {job.codigo} no tiene CRON"
                )

            return CronTrigger.from_crontab(
                job.expresion_cron,
                timezone=timezone,
            )

        if job.tipo == "INTERVALO":
            if not job.intervalo_segundos:
                raise ValueError(
                    f"El trabajo {job.codigo} no tiene intervalo"
                )

            return IntervalTrigger(
                seconds=job.intervalo_segundos,
                timezone=timezone,
                start_date=datetime.now(timezone),
            )

        raise ValueError(
            f"Tipo de trabajo no soportado: {job.tipo}"
        )