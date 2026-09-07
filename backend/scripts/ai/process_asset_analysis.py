import asyncio
from uuid import UUID

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.asset_analysis_processor import (
    AssetAnalysisProcessor,
)
from alphainvest.modules.ai.application.asset_analysis_runtime_service import (
    AssetAnalysisRuntimeService,
)
from alphainvest.modules.ai.application.asset_prediction_persistence_service import (
    AssetPredictionPersistenceService,
)
from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.price_forecast_inference_service import (
    PriceForecastInferenceService,
)
from alphainvest.modules.ai.application.price_forecast_model_runtime_service import (
    PriceForecastModelRuntimeService,
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
from alphainvest.modules.market.application.service import (
    MarketService,
)
from alphainvest.modules.market.infrastructure.exchange_trading_calendar import (
    ExchangeTradingCalendar,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

REQUEST_ID = UUID(
    "66702554-e0b4-4e16-85ea-c84b65e53552"
)



async def run() -> None:
    async with AsyncSessionFactory() as session:
        ai_repository = AIRepository(session)

        market_repository = MarketRepository(
            session
        )

        trend_runtime_service = (
            TrendModelRuntimeService(
                ai_repository
            )
        )

        feature_service = AIFeatureDataService(
            market_repository=market_repository,
            source_name="Yahoo Finance",
        )

        inference_service = TrendInferenceService(
            runtime_service=trend_runtime_service,
            feature_service=feature_service,
        )

        price_runtime_service = (
            PriceForecastModelRuntimeService(
                ai_repository
            )
        )

        market_service = MarketService(
            market_repository
        )

        price_forecast_service = (
            PriceForecastInferenceService(
                runtime_service=(
                    price_runtime_service
                ),
                market_service=market_service,
            )
        )

        asset_runtime_service = (
            AssetAnalysisRuntimeService(
                ai_repository=ai_repository,
                market_repository=market_repository,
            )
        )

        trading_calendar = (
            ExchangeTradingCalendar()
        )

        prediction_persistence_service = (
            AssetPredictionPersistenceService(
                repository=ai_repository,
                trading_calendar=trading_calendar,
            )
        )

        processor = AssetAnalysisProcessor(
            repository=ai_repository,
            inference_service=inference_service,
            price_forecast_service=(
                price_forecast_service
            ),
            runtime_service=(
                asset_runtime_service
            ),
            market_repository=market_repository,
            prediction_persistence_service=(
                prediction_persistence_service
            ),
        )

        result = await processor.process(
            request_id=REQUEST_ID,
        )

        prediction = result.prediction

        price_forecast = result.price_forecast

        if price_forecast is None:
            raise RuntimeError(
                "No se generó pronóstico de precio"
            )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — PROCESAMIENTO "
            "SOLICITUD ACTIVO"
        )
        print("=" * 72)

        print(f"Request ID: {result.request_id}")
        print(f"Base date:  {prediction.base_date}")
        print(
            f"Version:    {prediction.model_version}"
        )
        print(
            "Trend:      "
            f"{prediction.classification.value}"
        )
        print(
            f"Confidence: {prediction.confidence:.4f}"
        )

        print()
        print(
            "Bearish:    "
            f"{prediction.probabilities.bearish:.4f}"
        )
        print(
            "Neutral:    "
            f"{prediction.probabilities.neutral:.4f}"
        )
        print(
            "Bullish:    "
            f"{prediction.probabilities.bullish:.4f}"
        )

        print()
        print("PRICE FORECAST")
        print("-" * 60)

        print(
            f"Price base:  "
            f"{price_forecast.base_price:.8f}"
        )

        print(
            f"Return:      "
            f"{price_forecast.expected_return_percentage:.8f}%"
        )

        print(
            f"Predicted:   "
            f"{price_forecast.predicted_price:.8f}"
        )

        print(
            f"Version:     "
            f"{price_forecast.model_version}"
        )

        print("=" * 72)


async def main() -> None:
    try:
        await run()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())