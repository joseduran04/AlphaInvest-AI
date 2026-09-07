from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.asset_analysis_execution import (
    AssetAnalysisExecutionResult,
)
from alphainvest.modules.ai.infrastructure.models import (
    AssetPredictionModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.domain.trading_calendar import (
    TradingCalendar,
)


class AssetPredictionPersistenceService:
    """Construye y persiste una predicción ACTIVO."""

    def __init__(
        self,
        *,
        repository: AIRepository,
        trading_calendar: TradingCalendar,
    ) -> None:
        self._repository = repository
        self._trading_calendar = trading_calendar

    async def persist(
        self,
        *,
        request_id: UUID,
        asset_id: UUID,
        market_code: str,
        horizon: str,
        result: AssetAnalysisExecutionResult,
    ) -> AssetPredictionModel:
        price_forecast = result.price_forecast

        if price_forecast is None:
            raise ValueError(
                "El análisis no contiene "
                "pronóstico de precio"
            )

        trend = result.prediction

        if trend.base_date != price_forecast.base_date:
            raise ValueError(
                "Tendencia y pronóstico de precio "
                "deben compartir fecha base"
            )

        target_date = (
            self._trading_calendar.target_session(
                market_code=market_code,
                base_date=trend.base_date,
                horizon_sessions=(
                    price_forecast.horizon_sessions
                ),
            )
        )

        probabilities = trend.probabilities

        return await self._repository.create_asset_prediction(
            request_id=request_id,
            asset_id=asset_id,
            version_model_id=trend.version_id,
            base_date=trend.base_date,
            target_date=target_date,
            horizon=horizon,
            base_price=price_forecast.base_price,
            predicted_price=(
                price_forecast.predicted_price
            ),
            expected_return_percentage=(
                price_forecast
                .expected_return_percentage
            ),
            trend=trend.classification.value,
            confidence=Decimal(
                str(trend.confidence)
            ),
            bullish_probability=Decimal(
                str(probabilities.bullish)
            ),
            neutral_probability=Decimal(
                str(probabilities.neutral)
            ),
            bearish_probability=Decimal(
                str(probabilities.bearish)
            ),
            input_features={
                "trend_model_version": (
                    trend.model_version
                ),
                "price_model_version": (
                    price_forecast.model_version
                ),
                "price_source": (
                    price_forecast.source_name
                ),
            },
            model_output={
                "trend": (
                    trend.classification.value
                ),
                "confidence": (
                    str(trend.confidence)
                ),
                "expected_return_percentage": (
                    str(
                        price_forecast
                        .expected_return_percentage
                    )
                ),
                "price_forecast_version_id": str(
                    price_forecast.version_id
                ),
            },
        )