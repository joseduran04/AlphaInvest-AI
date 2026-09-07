from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.application.sentiment_inference_service import (
    SentimentInferenceService,
)
from alphainvest.modules.ai.application.sentiment_persistence_service import (
    SentimentPersistenceService,
)
from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisRequestStatus,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.news.infrastructure.mongodb_repository import (
    MongoNewsRepository,
)


class SentimentAnalysisProcessor:
    """Procesa una solicitud SENTIMIENTO pendiente."""

    MODEL_CODE = "ANALISIS_SENTIMIENTO"

    def __init__(
        self,
        *,
        ai_repository: AIRepository,
        market_repository: MarketRepository,
        mongo_repository: MongoNewsRepository,
        inference_service: SentimentInferenceService,
        persistence_service: SentimentPersistenceService,
    ) -> None:
        self._ai_repository = ai_repository
        self._market_repository = (
            market_repository
        )
        self._mongo_repository = (
            mongo_repository
        )
        self._inference_service = (
            inference_service
        )
        self._persistence_service = (
            persistence_service
        )

    async def process(
        self,
        *,
        request_id: UUID,
    ) -> None:
        request = (
            await self._ai_repository
            .get_analysis_request(
                request_id
            )
        )

        if request is None:
            raise ValueError(
                "La solicitud de análisis "
                "no existe"
            )

        if request.tipo_analisis != "SENTIMIENTO":
            raise ValueError(
                "La solicitud no corresponde "
                "a análisis SENTIMIENTO"
            )

        if (
            request.estado
            != AnalysisRequestStatus.PENDING.value
        ):
            raise ValueError(
                "La solicitud no se encuentra "
                "PENDIENTE"
            )

        await (
            self._ai_repository
            .increment_analysis_request_attempt(
                request
            )
        )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .RUNNING
                    .value
                ),
                progress=Decimal("10"),
                error_message=None,
            )
        )

        await self._ai_repository.commit()

        parameters = request.parametros

        if not isinstance(
            parameters,
            dict,
        ):
            raise ValueError(
                "La solicitud no contiene "
                "parámetros válidos"
            )

        asset_id = self._parse_uuid_parameter(
            parameters,
            "asset_id",
        )

        news_reference_id = (
            self._parse_uuid_parameter(
                parameters,
                "news_reference_id",
            )
        )

        news_reference = (
            await self._market_repository
            .get_news_reference(
                news_reference_id
            )
        )

        if news_reference is None:
            raise ValueError(
                "La referencia de noticia "
                "no existe"
            )

        if (
            news_reference.activo_id
            != asset_id
        ):
            raise ValueError(
                "La noticia no pertenece "
                "al activo solicitado"
            )

        existing = (
            await self._ai_repository
            .get_sentiment_analysis_by_request_and_news(
                request_id=request.id,
                news_reference_id=(
                    news_reference.id
                ),
            )
        )

        if existing is not None:
            raise ValueError(
                "La solicitud ya tiene "
                "un análisis de sentimiento "
                "persistido para esta noticia"
            )

        active_version = (
            await self._ai_repository
            .get_active_version_by_model_code(
                self.MODEL_CODE
            )
        )

        if active_version is None:
            raise ValueError(
                "No existe una versión activa "
                "de ANALISIS_SENTIMIENTO"
            )

        mongo_document = (
            await self._mongo_repository
            .get_by_document_id(
                news_reference.mongo_document_id
            )
        )

        if mongo_document is None:
            raise ValueError(
                "El documento de noticia "
                "no existe en MongoDB"
            )

        inference_text = (
            self._resolve_inference_text(
                mongo_document
            )
        )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .RUNNING
                    .value
                ),
                progress=Decimal("50"),
                error_message=None,
            )
        )

        prediction = (
            await self._inference_service
            .predict(
                version_id=active_version.id,
                text=inference_text,
            )
        )

        summary_value = mongo_document.get(
            "summary"
        )

        summary = (
            str(summary_value).strip()
            if summary_value is not None
            else None
        )

        if summary == "":
            summary = None

        await (
            self._persistence_service
            .persist_news_analysis(
                request_id=request.id,
                asset_id=asset_id,
                news_reference_id=(
                    news_reference.id
                ),
                mongo_document_id=(
                    news_reference
                    .mongo_document_id
                ),
                prediction=prediction,
                relevance=(
                    news_reference.relevancia
                ),
                language=(
                    news_reference.idioma
                ),
                summary=summary,
                content_date=(
                    news_reference
                    .fecha_publicacion
                ),
            )
        )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .COMPLETED
                    .value
                ),
                progress=Decimal("100"),
                error_message=None,
            )
        )

        await self._ai_repository.commit()

    @staticmethod
    def _parse_uuid_parameter(
        parameters: dict[str, object],
        key: str,
    ) -> UUID:
        raw_value = parameters.get(
            key
        )

        if not isinstance(
            raw_value,
            str,
        ):
            raise ValueError(
                f"El parámetro {key} "
                "no es válido"
            )

        try:
            return UUID(
                raw_value
            )

        except ValueError as error:
            raise ValueError(
                f"El parámetro {key} "
                "no contiene un UUID válido"
            ) from error

    @staticmethod
    def _resolve_inference_text(
        document: dict[str, object],
    ) -> str:
        summary = document.get(
            "summary"
        )

        if summary is not None:
            normalized_summary = str(
                summary
            ).strip()

            if normalized_summary:
                return normalized_summary

        title = document.get(
            "title"
        )

        if title is not None:
            normalized_title = str(
                title
            ).strip()

            if normalized_title:
                return normalized_title

        raise ValueError(
            "La noticia no contiene "
            "texto analizable"
        )