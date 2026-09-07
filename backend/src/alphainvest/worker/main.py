import asyncio
import logging
import signal

from alphainvest.core.config import get_settings
from alphainvest.infrastructure.database.session import (
    dispose_engine,
)
from alphainvest.worker.scheduler import (
    AlphaInvestScheduler,
)

logger = logging.getLogger(__name__)


async def run_worker() -> None:
    settings = get_settings()

    if not settings.worker_enabled:
        logger.warning(
            "El worker está deshabilitado. "
            "Usa APP_WORKER_ENABLED=true."
        )
        return

    scheduler = AlphaInvestScheduler(settings)

    try:
        if settings.worker_run_once:
            logger.info(
                "Iniciando ejecución única controlada"
            )

            await scheduler.run_job_now(
                settings.worker_run_once_job
            )

            logger.info(
                "Ejecución única finalizada"
            )
            return

        registered = await scheduler.load_jobs()

        logger.info(
            "Worker iniciado con %s trabajo(s)",
            registered,
        )

        if settings.worker_run_on_startup:
            logger.info(
                "Ejecutando sincronización inicial"
            )
            await scheduler.run_job_now(
                "ACTUALIZAR_PRECIOS_DIARIOS"
            )

        scheduler.start()

        stop_event = asyncio.Event()
        loop = asyncio.get_running_loop()

        def request_shutdown() -> None:
            stop_event.set()

        for current_signal in (
            signal.SIGINT,
            signal.SIGTERM,
        ):
            try:
                loop.add_signal_handler(
                    current_signal,
                    request_shutdown,
                )
            except NotImplementedError:
                pass

        await stop_event.wait()

    finally:
        scheduler.shutdown()
        await dispose_engine()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s %(levelname)s "
            "%(name)s %(message)s"
        ),
    )

    asyncio.run(run_worker())


if __name__ == "__main__":
    main()