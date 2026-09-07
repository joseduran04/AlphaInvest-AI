import asyncio

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.price_forecast_inference_service import (
    PriceForecastInferenceService,
)
from alphainvest.modules.ai.application.price_forecast_model_runtime_service import (
    PriceForecastModelRuntimeService,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.application.service import (
    MarketService,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

MODEL_CODE = "PRONOSTICO_PRECIO"
MODEL_VERSION = "0.1.0"

SYMBOL = "AAPL"
SOURCE_NAME = "Yahoo Finance"


async def run() -> None:
    async with AsyncSessionFactory() as session:
        ai_repository = AIRepository(session)

        market_repository = MarketRepository(
            session
        )

        model = (
            await ai_repository
            .get_model_by_code(
                MODEL_CODE
            )
        )

        if model is None:
            raise RuntimeError(
                f"No existe {MODEL_CODE}"
            )

        versions = (
            await ai_repository
            .list_model_versions(
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

        asset = (
            await market_repository
            .get_active_asset_by_symbol(
                SYMBOL
            )
        )

        if asset is None:
            raise RuntimeError(
                f"No existe el activo {SYMBOL}"
            )

        source = (
            await market_repository
            .get_financial_source_by_name(
                name=SOURCE_NAME
            )
        )

        if source is None:
            raise RuntimeError(
                f"No existe la fuente "
                f"{SOURCE_NAME}"
            )

        runtime_service = (
            PriceForecastModelRuntimeService(
                ai_repository
            )
        )

        market_service = MarketService(
            market_repository
        )

        inference_service = (
            PriceForecastInferenceService(
                runtime_service=runtime_service,
                market_service=market_service,
            )
        )

        result = (
            await inference_service
            .predict_latest(
                version_id=version.id,
                asset_id=asset.id,
                source_id=source.id,
            )
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — INFERENCIA "
            "PRONOSTICO_PRECIO"
        )
        print("=" * 72)

        print(
            f"Fecha base:       "
            f"{result.base_date}"
        )

        print(
            f"Versión:          "
            f"{result.model_version}"
        )

        print(
            f"Horizonte:        "
            f"{result.horizon_sessions} sesiones"
        )

        print(
            f"Precio base:      "
            f"{result.base_price:.8f}"
        )

        print(
            "Retorno esperado: "
            f"{result.expected_return_percentage:.8f}%"
        )

        print(
            f"Precio predicho:  "
            f"{result.predicted_price:.8f}"
        )

        print(
            f"Fuente:           "
            f"{result.source_name}"
        )

        print("=" * 72)


async def main() -> None:
    try:
        await run()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())