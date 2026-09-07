import asyncio
from datetime import date
from uuid import UUID

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.trend_inference_service import (
    TrendInferenceService,
)
from alphainvest.modules.ai.application.trend_model_runtime_service import (
    TrendModelRuntimeService,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

VERSION_ID = UUID(
    "942d31f4-dc1c-4c85-936c-23ba76a64771"
)

ASSET_ID = UUID(
    "0475ba44-833c-4f32-a582-f22d0f968d15"
)

SOURCE_NAME = "Yahoo Finance"


async def run() -> None:
    async with AsyncSessionFactory() as session:
        ai_repository = AIRepository(session)
        market_repository = MarketRepository(session)

        runtime_service = TrendModelRuntimeService(
            ai_repository
        )

        feature_service = AIFeatureDataService(
            market_repository=market_repository,
            source_name=SOURCE_NAME,
        )

        inference_service = TrendInferenceService(
            runtime_service=runtime_service,
            feature_service=feature_service,
        )

        result = await inference_service.predict_latest(
            version_id=VERSION_ID,
            asset_id=ASSET_ID,
            start_date=date(2000, 1, 1),
            end_date=date(2026, 8, 14),
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — INFERENCIA "
            "PREDICCION_TENDENCIA"
        )
        print("=" * 72)

        print(f"Fecha base:  {result.base_date}")
        print(
            f"Versión:     {result.model_version}"
        )
        print(
            f"Tendencia:   {result.classification.value}"
        )
        print(
            f"Confianza:   {result.confidence:.4f}"
        )

        print()
        print("Probabilidades")
        print(
            "BAJISTA:     "
            f"{result.probabilities.bearish:.4f}"
        )
        print(
            "NEUTRAL:     "
            f"{result.probabilities.neutral:.4f}"
        )
        print(
            "ALCISTA:     "
            f"{result.probabilities.bullish:.4f}"
        )

        print()
        print(
            f"Suma:        "
            f"{result.probabilities.total:.4f}"
        )

        print("=" * 72)


async def main() -> None:
    try:
        await run()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())