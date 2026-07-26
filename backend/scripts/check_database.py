import asyncio

from alphainvest.infrastructure.database.health import check_database
from alphainvest.infrastructure.database.session import dispose_engine, engine


async def main() -> None:
    result = await check_database(engine)
    print(f"database={result.status} latency_ms={result.latency_ms} error={result.error}")
    await dispose_engine()
    if result.status != "up":
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
