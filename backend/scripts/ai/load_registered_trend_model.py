import asyncio
from uuid import UUID

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.trend_model_runtime_service import (
    TrendModelRuntimeService,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)

VERSION_ID = UUID(
    "942d31f4-dc1c-4c85-936c-23ba76a64771"
)


async def run() -> None:
    async with AsyncSessionFactory() as session:
        repository = AIRepository(session)

        service = TrendModelRuntimeService(
            repository
        )

        loaded = await service.load_version(
            version_id=VERSION_ID
        )

        print()
        print("=" * 72)
        print("ALPHAINVEST AI — LOAD REGISTERED MODEL")
        print("=" * 72)
        print(f"Version ID: {loaded.version_id}")
        print(f"Model ID:   {loaded.model_id}")
        print(f"Version:    {loaded.version}")
        print(
            f"Artifact:   "
            f"{loaded.artifact_path.as_posix()}"
        )
        print(f"SHA-256:    {loaded.checksum}")
        print("Status:     MODEL LOAD OK")
        print("=" * 72)


async def main() -> None:
    try:
        await run()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())