import logging
from collections.abc import Awaitable, Callable
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
    """Carga y ejecuta los trabajos definidos en PostgreSQL."""

    def __init__(
        self,
        settings: Settings,
    ) -> None:
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
                    self._execute_with_retries,
                    trigger=trigger,
                    id=job.codigo,
                    name=job.nombre,
                    kwargs={
                        "job_code": job.codigo,
                        "worker_job": worker_job,
                        "max_retries": (
                            job.maximo_reintentos
                        ),
                    },
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

                next_execution = (
                    trigger.get_next_fire_time(
                        previous_fire_time=None,
                        now=datetime.now(
                            trigger_timezone
                        ),
                    )
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
            self._scheduler.shutdown(
                wait=False
            )

    async def run_job_now(
        self,
        job_code: str,
    ) -> None:
        """Ejecuta inmediatamente un trabajo registrado."""

        worker_job = WORKER_JOB_REGISTRY.get(
            job_code
        )

        if worker_job is None:
            raise ValueError(
                f"Trabajo no implementado: {job_code}"
            )

        async with AsyncSessionFactory() as session:
            repository = OperationRepository(session)

            job = await repository.get_job_by_code(
                job_code
            )

        if job is None:
            raise ValueError(
                "Trabajo no registrado o inactivo: "
                f"{job_code}"
            )

        await self._execute_with_retries(
            job_code=job.codigo,
            worker_job=worker_job,
            max_retries=job.maximo_reintentos,
        )

    async def _execute_with_retries(
        self,
        *,
        job_code: str,
        worker_job: Callable[
            [Settings],
            Awaitable[None],
        ],
        max_retries: int,
    ) -> None:
        """Ejecuta un trabajo y aplica reintentos técnicos."""

        max_attempts = 1 + max_retries

        for attempt_number in range(
            1,
            max_attempts + 1,
        ):
            try:
                logger.info(
                    (
                        "Ejecutando trabajo %s "
                        "intento=%s/%s"
                    ),
                    job_code,
                    attempt_number,
                    max_attempts,
                )

                await worker_job(
                    self._settings
                )

                return

            except Exception:
                if attempt_number >= max_attempts:
                    logger.exception(
                        (
                            "Trabajo %s falló "
                            "definitivamente tras "
                            "%s intento(s)"
                        ),
                        job_code,
                        attempt_number,
                    )

                    raise

                logger.exception(
                    (
                        "Trabajo %s falló en "
                        "intento=%s/%s; "
                        "se reintentará"
                    ),
                    job_code,
                    attempt_number,
                    max_attempts,
                )

    @staticmethod
    def _build_trigger(
        job: ScheduledJobModel,
    ) -> CronTrigger | IntervalTrigger:
        timezone = ZoneInfo(
            job.zona_horaria
        )

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
                    f"El trabajo {job.codigo} "
                    "no tiene intervalo"
                )

            return IntervalTrigger(
                seconds=job.intervalo_segundos,
                timezone=timezone,
                start_date=datetime.now(
                    timezone
                ),
            )

        raise ValueError(
            "Tipo de trabajo no soportado: "
            f"{job.tipo}"
        )