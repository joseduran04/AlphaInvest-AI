from uuid import UUID

from alphainvest.modules.ai.domain.exceptions import (
    AIModelNotFoundError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.domain.loaded_price_forecast_model import (
    LoadedPriceForecastModel,
)
from alphainvest.modules.ai.infrastructure.price_forecast_model_loader import (
    PriceForecastModelLoader,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)


class PriceForecastModelRuntimeService:
    """Resuelve versiones registradas de pronóstico de precio."""

    def __init__(
        self,
        repository: AIRepository,
    ) -> None:
        self._repository = repository

    async def load_version(
        self,
        *,
        version_id: UUID,
    ) -> LoadedPriceForecastModel:
        version = (
            await self._repository.get_model_version(
                version_id
            )
        )

        if version is None:
            raise ModelVersionNotFoundError(
                "La versión del modelo solicitada "
                "no existe"
            )

        model = await self._repository.get_model(
            version.modelo_id
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo asociado con la versión "
                "no existe"
            )

        if model.codigo != "PRONOSTICO_PRECIO":
            raise ValueError(
                "La versión solicitada no pertenece "
                "al modelo PRONOSTICO_PRECIO"
            )

        return PriceForecastModelLoader.load(
            version
        )