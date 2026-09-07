from dataclasses import dataclass
from time import perf_counter
from typing import Any

from pymongo import AsyncMongoClient


@dataclass(frozen=True, slots=True)
class MongoHealth:
    status: str
    latency_ms: float | None
    error: str | None = None


async def check_mongodb(
    client: AsyncMongoClient[
        dict[str, Any]
    ],
) -> MongoHealth:
    started = perf_counter()

    try:
        await client.admin.command(
            {"ping": 1}
        )

        latency = round(
            (
                perf_counter()
                - started
            )
            * 1000,
            2,
        )

        return MongoHealth(
            status="up",
            latency_ms=latency,
        )

    except Exception as exc:
        return MongoHealth(
            status="down",
            latency_ms=None,
            error=exc.__class__.__name__,
        )