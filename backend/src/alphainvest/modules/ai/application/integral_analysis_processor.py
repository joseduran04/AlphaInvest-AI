from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.application.recommendation_processor import (
    RecommendationProcessor,
)
from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisRequestStatus,
    AnalysisType,
)
from alphainvest.modules.ai.infrastructure.models import (
    AnalysisRequestModel,
    RecommendationModel,
    SentimentAnalysisModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)


class IntegralAnalysisProcessor:
    """Orquesta una solicitud de análisis INTEGRAL."""

    def __init__(
        self,
        *,
        ai_repository: AIRepository,
        recommendation_processor: RecommendationProcessor,
    ) -> None:
        self._ai_repository = ai_repository
        self._recommendation_processor = (
            recommendation_processor
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
                "La solicitud de análisis integral "
                "no existe"
            )

        if (
            request.tipo_analisis
            != AnalysisType.INTEGRAL.value
        ):
            raise ValueError(
                "La solicitud no corresponde "
                "a INTEGRAL"
            )

        if (
            request.estado
            != AnalysisRequestStatus.PENDING.value
        ):
            raise ValueError(
                "La solicitud INTEGRAL "
                "no se encuentra PENDIENTE"
            )

        parameters = request.parametros

        if not isinstance(
            parameters,
            dict,
        ):
            raise ValueError(
                "La solicitud INTEGRAL no contiene "
                "parámetros válidos"
            )

        asset_id = self._parse_uuid_parameter(
            parameters,
            "asset_id",
        )

        prediction_request_id = (
            self._parse_uuid_parameter(
                parameters,
                "prediction_request_id",
            )
        )

        sentiment_request_ids = (
            self._parse_uuid_list_parameter(
                parameters,
                "sentiment_request_ids",
            )
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

        prediction_request = (
            await self._ai_repository
            .get_analysis_request_for_user(
                request_id=prediction_request_id,
                user_id=request.usuario_id,
            )
        )

        if prediction_request is None:
            raise ValueError(
                "La solicitud ACTIVO asociada "
                "no existe"
            )

        if (
            prediction_request.tipo_analisis
            != AnalysisType.ASSET.value
        ):
            raise ValueError(
                "prediction_request_id no corresponde "
                "a una solicitud ACTIVO"
            )

        if (
            prediction_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise ValueError(
                "La solicitud ACTIVO asociada "
                "no está COMPLETADA"
            )

        prediction = (
            await self._ai_repository
            .get_asset_prediction_by_request(
                request_id=prediction_request_id
            )
        )

        if prediction is None:
            raise ValueError(
                "La solicitud ACTIVO asociada "
                "no tiene una predicción persistida"
            )

        if prediction.activo_id != asset_id:
            raise ValueError(
                "La predicción ACTIVO no pertenece "
                "al activo del análisis INTEGRAL"
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
                progress=Decimal("30"),
                error_message=None,
            )
        )

        sentiment_analyses: list[
            SentimentAnalysisModel
        ] = []

        for sentiment_request_id in (
            sentiment_request_ids
        ):
            sentiment_request = (
                await self._ai_repository
                .get_analysis_request_for_user(
                    request_id=sentiment_request_id,
                    user_id=request.usuario_id,
                )
            )

            if sentiment_request is None:
                raise ValueError(
                    "Una solicitud SENTIMIENTO "
                    "asociada no existe"
                )

            if (
                sentiment_request.tipo_analisis
                != AnalysisType.SENTIMENT.value
            ):
                raise ValueError(
                    "Una solicitud asociada no "
                    "corresponde a SENTIMIENTO"
                )

            if (
                sentiment_request.estado
                != AnalysisRequestStatus.COMPLETED.value
            ):
                raise ValueError(
                    "Una solicitud SENTIMIENTO "
                    "asociada no está COMPLETADA"
                )

            sentiment_analysis = (
                await self._ai_repository
                .get_sentiment_analysis_by_request(
                    request_id=sentiment_request_id
                )
            )

            if sentiment_analysis is None:
                raise ValueError(
                    "Una solicitud SENTIMIENTO "
                    "no tiene resultado persistido"
                )

            if sentiment_analysis.activo_id != asset_id:
                raise ValueError(
                    "Un análisis SENTIMIENTO no "
                    "pertenece al activo del INTEGRAL"
                )

            sentiment_analyses.append(
                sentiment_analysis
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

        recommendation_request_id = (
            self._get_optional_uuid_parameter(
                parameters,
                "recommendation_request_id",
            )
        )

        if recommendation_request_id is None:
            created_recommendation_request = (
                await self._ai_repository
                .create_analysis_request(
                    user_id=request.usuario_id,
                    analysis_type=(
                        AnalysisType
                        .RECOMMENDATION
                        .value
                    ),
                    horizon=request.horizonte,
                    reference_date=(
                        request.fecha_referencia
                    ),
                    parameters={
                        "asset_id": str(asset_id),
                        "prediction_request_id": str(
                            prediction_request_id
                        ),
                        "integral_request_id": str(
                            request.id
                        ),
                    },
                    portfolio_id=(
                        request.portafolio_id
                    ),
                )
            )

            recommendation_request_id = (
                created_recommendation_request.id
            )

            updated_parameters = dict(
                parameters
            )

            updated_parameters[
                "recommendation_request_id"
            ] = str(
                recommendation_request_id
            )

            await (
                self._ai_repository
                .update_analysis_request_parameters(
                    request,
                    parameters=updated_parameters,
                )
            )

            parameters = updated_parameters

            await self._ai_repository.commit()

        recommendation_request = (
            await self._ai_repository
            .get_analysis_request(
                recommendation_request_id
            )
        )

        if recommendation_request is None:
            raise ValueError(
                "La solicitud RECOMENDACION hija "
                "no existe"
            )

        if (
            recommendation_request.usuario_id
            != request.usuario_id
        ):
            raise ValueError(
                "La solicitud RECOMENDACION hija "
                "pertenece a otro usuario"
            )

        if (
            recommendation_request.tipo_analisis
            != AnalysisType.RECOMMENDATION.value
        ):
            raise ValueError(
                "La solicitud hija no corresponde "
                "a RECOMENDACION"
            )

        if (
            recommendation_request.estado
            == AnalysisRequestStatus.PENDING.value
        ):
            await (
                self._recommendation_processor
                .process(
                    request_id=(
                        recommendation_request.id
                    )
                )
            )

            refreshed_recommendation_request = (
                await self._ai_repository
                .get_analysis_request(
                    recommendation_request.id
                )
            )

            if refreshed_recommendation_request is None:
                raise ValueError(
                    "No fue posible recuperar "
                    "la solicitud RECOMENDACION hija"
                )

            recommendation_request = (
                refreshed_recommendation_request
            )

        if (
            recommendation_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise ValueError(
                "La solicitud RECOMENDACION hija "
                "no finalizó correctamente"
            )

        recommendation = (
            await self._ai_repository
            .get_recommendation_by_request(
                request_id=(
                    recommendation_request.id
                )
            )
        )

        if recommendation is None:
            raise ValueError(
                "La solicitud RECOMENDACION hija "
                "no tiene resultado persistido"
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
                progress=Decimal("80"),
                error_message=None,
            )
        )

        existing_evidences = (
            await self._ai_repository
            .list_analysis_evidence_for_recommendation(
                recommendation_id=recommendation.id
            )
        )

        existing_sentiment_sources = {
            evidence.identificador_origen
            for evidence in existing_evidences
            if (
                evidence.tipo_evidencia
                == "SENTIMIENTO"
                and evidence.entidad_origen
                == "ai.analisis_sentimiento"
                and evidence.identificador_origen
                is not None
            )
        }

        for sentiment_analysis in (
            sentiment_analyses
        ):
            if (
                str(sentiment_analysis.id)
                in existing_sentiment_sources
            ):
                continue

            await (
                self._create_sentiment_evidence(
                    integral_request=request,
                    recommendation_request=(
                        recommendation_request
                    ),
                    recommendation=(
                        recommendation
                    ),
                    sentiment_analysis=(
                        sentiment_analysis
                    ),
                )
            )

            existing_sentiment_sources.add(
                str(sentiment_analysis.id)
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

    async def _create_sentiment_evidence(
        self,
        *,
        integral_request: AnalysisRequestModel,
        recommendation_request: AnalysisRequestModel,
        recommendation: RecommendationModel,
        sentiment_analysis: SentimentAnalysisModel,
    ) -> None:
        sentiment = (
            sentiment_analysis.sentimiento
        )

        contribution = {
            "POSITIVO": "POSITIVA",
            "NEUTRAL": "NEUTRAL",
            "NEGATIVO": "NEGATIVA",
        }.get(
            sentiment,
            "NEUTRAL",
        )

        confidence = str(
            sentiment_analysis.confianza
        )

        await (
            self._ai_repository
            .create_analysis_evidence(
                request_id=(
                    recommendation_request.id
                ),
                recommendation_id=(
                    recommendation.id
                ),
                prediction_id=None,
                evidence_type="SENTIMIENTO",
                source_entity=(
                    "ai.analisis_sentimiento"
                ),
                source_identifier=str(
                    sentiment_analysis.id
                ),
                description=(
                    "Análisis de sentimiento "
                    "incorporado por la solicitud "
                    "INTEGRAL "
                    f"{integral_request.id}"
                ),
                numeric_value=(
                    sentiment_analysis.puntuacion
                ),
                unit=None,
                weight=(
                    sentiment_analysis.relevancia
                ),
                contribution=contribution,
                data={
                    "integral_request_id": str(
                        integral_request.id
                    ),
                    "sentiment": sentiment,
                    "confidence": confidence,
                },
                evidence_date=(
                    sentiment_analysis.fecha_analisis
                ),
            )
        )

    @staticmethod
    def _parse_uuid_parameter(
        parameters: dict[str, object],
        key: str,
    ) -> UUID:
        value = parameters.get(
            key
        )

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"El parámetro {key} "
                "no es válido"
            )

        try:
            return UUID(value)

        except ValueError as error:
            raise ValueError(
                f"El parámetro {key} "
                "no contiene un UUID válido"
            ) from error

    @staticmethod
    def _get_optional_uuid_parameter(
        parameters: dict[str, object],
        key: str,
    ) -> UUID | None:
        value = parameters.get(
            key
        )

        if value is None:
            return None

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                f"El parámetro {key} "
                "no es válido"
            )

        try:
            return UUID(value)

        except ValueError as error:
            raise ValueError(
                f"El parámetro {key} "
                "no contiene un UUID válido"
            ) from error

    @staticmethod
    def _parse_uuid_list_parameter(
        parameters: dict[str, object],
        key: str,
    ) -> list[UUID]:
        value = parameters.get(
            key
        )

        if value is None:
            return []

        if not isinstance(
            value,
            list,
        ):
            raise ValueError(
                f"El parámetro {key} "
                "no es una lista válida"
            )

        result: list[UUID] = []

        for item in value:
            if not isinstance(
                item,
                str,
            ):
                raise ValueError(
                    f"El parámetro {key} "
                    "contiene un valor inválido"
                )

            try:
                result.append(
                    UUID(item)
                )

            except ValueError as error:
                raise ValueError(
                    f"El parámetro {key} "
                    "contiene un UUID inválido"
                ) from error

        if len(result) != len(set(result)):
            raise ValueError(
                f"El parámetro {key} "
                "contiene UUID duplicados"
            )

        return result