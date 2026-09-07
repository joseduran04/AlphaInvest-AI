import asyncio

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.price_forecast_model_runtime_service import (
    PriceForecastModelRuntimeService,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)

MODEL_CODE = "PRONOSTICO_PRECIO"
MODEL_VERSION = "0.1.0"


async def run() -> None:
    async with AsyncSessionFactory() as session:
        repository = AIRepository(session)

        model = await repository.get_model_by_code(
            MODEL_CODE
        )

        if model is None:
            raise RuntimeError(
                f"No existe {MODEL_CODE}"
            )

        versions = (
            await repository.list_model_versions(
                model_id=model.id
            )
        )

        version = next(
            (
                item
                for item in versions
                if item.version == MODEL_VERSION
            ),
            None,
        )

        if version is None:
            raise RuntimeError(
                f"No existe la versión "
                f"{MODEL_VERSION}"
            )

        service = (
            PriceForecastModelRuntimeService(
                repository
            )
        )

        loaded = await service.load_version(
            version_id=version.id
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — LOAD "
            "REGISTERED PRICE FORECAST"
        )
        print("=" * 72)

        print(
            f"Version ID:    "
            f"{loaded.version_id}"
        )

        print(
            f"Model ID:      "
            f"{loaded.model_id}"
        )

        print(
            f"Version:       "
            f"{loaded.version}"
        )

        print(
            f"Artifact:      "
            f"{loaded.artifact_path.as_posix()}"
        )

        print(
            f"SHA-256:       "
            f"{loaded.checksum}"
        )

        print(
            f"Algorithm:     "
            f"{loaded.algorithm}"
        )

        print(
            f"Horizon:       "
            f"{loaded.horizon_sessions}"
        )

        print(
            "Median return:  "
            f"{loaded.median_return_percentage}%"
        )

        print(
            "Status:         MODEL LOAD OK"
        )

        print("=" * 72)


async def main() -> None:
    try:
        await run()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())