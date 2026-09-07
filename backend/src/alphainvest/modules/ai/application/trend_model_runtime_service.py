from uuid import UUID

from alphainvest.modules.ai.domain.exceptions import (
    AIModelNotFoundError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.domain.loaded_model import (
    LoadedTrendModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.ai.infrastructure.trend_model_loader import (
    TrendModelLoader,
)


class TrendModelRuntimeService:
    """Resuelve y carga versiones de tendencia para ejecución."""

    def __init__(
        self,
        repository: AIRepository,
    ) -> None:
        self._repository = repository

    async def load_version(
        self,
        *,
        version_id: UUID,
    ) -> LoadedTrendModel:
        version = await self._repository.get_model_version(
            version_id
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

        if model.codigo != "PREDICCION_TENDENCIA":
            raise ValueError(
                "La versión solicitada no pertenece "
                "al modelo PREDICCION_TENDENCIA"
            )

        return TrendModelLoader.load(
            version
        )