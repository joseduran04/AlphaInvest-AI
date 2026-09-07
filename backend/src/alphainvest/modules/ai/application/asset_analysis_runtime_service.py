from alphainvest.modules.ai.domain.asset_analysis_runtime import (
    AssetAnalysisRuntime,
)
from alphainvest.modules.ai.domain.exceptions import (
    AIModelNotFoundError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.infrastructure.models import (
    ModelVersionModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.domain.exceptions import (
    FinancialSourceNotFoundError,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)


class AssetAnalysisRuntimeService:
    """Resuelve dependencias registradas para análisis ACTIVO."""

    TREND_MODEL_CODE = "PREDICCION_TENDENCIA"
    TREND_VERSION = "0.1.0"

    PRICE_MODEL_CODE = "PRONOSTICO_PRECIO"
    PRICE_VERSION = "0.1.0"

    PRICE_SOURCE_NAME = "Yahoo Finance"

    def __init__(
        self,
        *,
        ai_repository: AIRepository,
        market_repository: MarketRepository,
    ) -> None:
        self._ai_repository = ai_repository
        self._market_repository = market_repository

    async def resolve(
        self,
    ) -> AssetAnalysisRuntime:
        trend_version = await self._resolve_version(
            model_code=self.TREND_MODEL_CODE,
            version=self.TREND_VERSION,
        )

        price_version = await self._resolve_version(
            model_code=self.PRICE_MODEL_CODE,
            version=self.PRICE_VERSION,
        )

        source = (
            await self._market_repository
            .get_financial_source_by_name(
                name=self.PRICE_SOURCE_NAME
            )
        )

        if source is None:
            raise FinancialSourceNotFoundError(
                "No existe la fuente financiera "
                f"{self.PRICE_SOURCE_NAME}"
            )

        return AssetAnalysisRuntime(
            trend_version_id=trend_version.id,
            price_forecast_version_id=price_version.id,
            price_source_id=source.id,
            trend_version=trend_version.version,
            price_forecast_version=price_version.version,
            price_source_name=source.nombre,
        )

    async def _resolve_version(
        self,
        *,
        model_code: str,
        version: str,
    ) -> ModelVersionModel:
        model = (
            await self._ai_repository
            .get_model_by_code(
                model_code
            )
        )

        if model is None:
            raise AIModelNotFoundError(
                f"No existe el modelo {model_code}"
            )

        versions = (
            await self._ai_repository
            .list_model_versions(
                model_id=model.id
            )
        )

        resolved = next(
            (
                item
                for item in versions
                if item.version == version
            ),
            None,
        )

        if resolved is None:
            raise ModelVersionNotFoundError(
                f"No existe {model_code} "
                f"versión {version}"
            )

        return resolved

