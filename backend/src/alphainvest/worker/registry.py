from collections.abc import Awaitable, Callable

from alphainvest.core.config import Settings
from alphainvest.worker.jobs.market_prices import (
    synchronize_configured_market_prices,
)

WorkerJob = Callable[[Settings], Awaitable[None]]

WORKER_JOB_REGISTRY: dict[str, WorkerJob] = {
    "ACTUALIZAR_PRECIOS_DIARIOS": (
        synchronize_configured_market_prices
    ),
}