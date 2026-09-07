from uuid import UUID

from alphainvest.modules.ai.domain.exceptions import (
    AIModelNotFoundError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.domain.loaded_sentiment_model import (
    LoadedSentimentModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.ai.infrastructure.sentiment_model_loader import (
    SentimentModelLoader,
)


class SentimentModelRuntimeService:
    """Resuelve versiones registradas del modelo NLP."""

    MODEL_CODE = "ANALISIS_SENTIMIENTO"

    def __init__(
        self,
        repository: AIRepository,
    ) -> None:
        self._repository = repository

    async def load_version(
        self,
        *,
        version_id: UUID,
    ) -> LoadedSentimentModel:
        version = (
            await self._repository
            .get_model_version(
                version_id
            )
        )

        if version is None:
            raise ModelVersionNotFoundError(
                "La versión del modelo solicitada "
                "no existe"
            )

        model = (
            await self._repository
            .get_model(
                version.modelo_id
            )
        )

        if model is None:
            raise AIModelNotFoundError(
                "El modelo asociado con la versión "
                "no existe"
            )

        if (
            model.codigo
            != self.MODEL_CODE
        ):
            raise ValueError(
                "La versión solicitada no pertenece "
                "al modelo ANALISIS_SENTIMIENTO"
            )

        return SentimentModelLoader.load(
            version
        )