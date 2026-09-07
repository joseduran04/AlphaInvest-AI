from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.application.price_forecast_model_runtime_service import (
    PriceForecastModelRuntimeService,
)
from alphainvest.modules.ai.domain.price_forecast_prediction import (
    PriceForecastPredictionResult,
)
from alphainvest.modules.market.application.service import (
    MarketService,
)


class PriceForecastInferenceService:
    """Ejecuta inferencias del pronóstico de precio."""

    ONE_HUNDRED = Decimal("100")

    def __init__(
        self,
        *,
        runtime_service: PriceForecastModelRuntimeService,
        market_service: MarketService,
    ) -> None:
        self._runtime_service = runtime_service
        self._market_service = market_service

    async def predict_latest(
        self,
        *,
        version_id: UUID,
        asset_id: UUID,
        source_id: UUID,
    ) -> PriceForecastPredictionResult:
        loaded = await self._runtime_service.load_version(
            version_id=version_id
        )

        latest = (
            await self._market_service
            .get_latest_asset_price(
                asset_id=asset_id,
                source_id=source_id,
            )
        )

        price = latest.price

        base_price = (
            price.adjusted_close
            if price.adjusted_close is not None
            else price.close
        )

        if base_price <= 0:
            raise ValueError(
                "El precio base debe ser "
                "mayor que cero"
            )

        expected_return = (
            loaded.median_return_percentage
        )

        predicted_price = (
            base_price
            * (
                Decimal("1")
                + (
                    expected_return
                    / self.ONE_HUNDRED
                )
            )
        )

        return PriceForecastPredictionResult(
            asset_id=asset_id,
            base_date=price.date,
            version_id=loaded.version_id,
            model_id=loaded.model_id,
            model_version=loaded.version,
            horizon_sessions=(
                loaded.horizon_sessions
            ),
            base_price=base_price,
            predicted_price=predicted_price,
            expected_return_percentage=(
                expected_return
            ),
            source_name=loaded.source_name,
        )