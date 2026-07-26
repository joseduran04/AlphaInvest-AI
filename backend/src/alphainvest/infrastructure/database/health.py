from dataclasses import dataclass
from time import perf_counter

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


@dataclass(frozen=True, slots=True)
class DatabaseHealth:
    status: str
    latency_ms: float | None
    error: str | None = None


async def check_database(engine: AsyncEngine) -> DatabaseHealth:
    started = perf_counter()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        latency = round((perf_counter() - started) * 1000, 2)
        return DatabaseHealth(status="up", latency_ms=latency)
    except Exception as exc:  # Se transforma en estado, no se filtran credenciales.
        return DatabaseHealth(
            status="down",
            latency_ms=None,
            error=exc.__class__.__name__,
        )
