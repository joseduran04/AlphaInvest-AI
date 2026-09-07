from uuid import UUID

from sqlalchemy.exc import IntegrityError

from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisHorizon,
    AnalysisRequestStatus,
    AnalysisType,
)
from alphainvest.modules.ai.domain.exceptions import (
    AnalysisRequestInvalidParametersError,
    AnalysisRequestInvalidStateError,
    AnalysisRequestNotFoundError,
    AnalysisRequestPersistenceError,
    AnalysisResultNotFoundError,
    AnalysisResultNotReadyError,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.ai.presentation.schemas import (
    AnalysisRequestResponse,
    AssetAnalysisRequestCreate,
    AssetAnalysisResultResponse,
    AssetPredictionProbabilitiesResponse,
    IntegralAnalysisRequestCreate,
    RecommendationAssetResponse,
    RecommendationEvidenceResponse,
    RecommendationRequestCreate,
    RecommendationResultResponse,
    SentimentAnalysisRequestCreate,
)


class AnalysisRequestService:
    """Casos de uso para solicitudes de análisis."""

    def __init__(
        self,
        repository: AIRepository,
    ) -> None:
        self._repository = repository

    async def create_asset_request(
        self,
        *,
        user_id: UUID,
        request: AssetAnalysisRequestCreate,
    ) -> AnalysisRequestResponse:
        parameters: dict[str, object] = {
            "asset_id": str(request.asset_id),
        }

        try:
            analysis_request = (
                await self._repository
                .create_analysis_request(
                    user_id=user_id,
                    analysis_type=(
                        AnalysisType.ASSET.value
                    ),
                    horizon=request.horizon.value,
                    reference_date=(
                        request.reference_date
                    ),
                    parameters=parameters,
                )
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise AnalysisRequestPersistenceError(
                "No fue posible registrar "
                "la solicitud de análisis"
            ) from error

        return AnalysisRequestResponse.model_validate(
            analysis_request
        )

    async def create_sentiment_request(
        self,
        *,
        user_id: UUID,
        request: SentimentAnalysisRequestCreate,
    ) -> AnalysisRequestResponse:
        parameters: dict[str, object] = {
            "asset_id": str(
                request.asset_id
            ),
            "news_reference_id": str(
                request.news_reference_id
            ),
        }

        try:
            analysis_request = (
                await self._repository
                .create_analysis_request(
                    user_id=user_id,
                    analysis_type=(
                        AnalysisType.SENTIMENT.value
                    ),
                    horizon=None,
                    reference_date=(
                        request.reference_date
                    ),
                    parameters=parameters,
                )
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise AnalysisRequestPersistenceError(
                "No fue posible registrar "
                "la solicitud de sentimiento"
            ) from error

        return AnalysisRequestResponse.model_validate(
            analysis_request
        )

    async def create_recommendation_request(
        self,
        *,
        user_id: UUID,
        request: RecommendationRequestCreate,
    ) -> AnalysisRequestResponse:
        prediction_request = (
            await self._repository
            .get_analysis_request_for_user(
                request_id=(
                    request.prediction_request_id
                ),
                user_id=user_id,
            )
        )

        if prediction_request is None:
            raise AnalysisRequestNotFoundError(
                "La solicitud ACTIVO asociada "
                "no existe"
            )

        if (
            prediction_request.tipo_analisis
            != AnalysisType.ASSET.value
        ):
            raise AnalysisRequestInvalidParametersError(
                "prediction_request_id no corresponde "
                "a una solicitud ACTIVO"
            )

        if (
            prediction_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise AnalysisRequestInvalidStateError(
                "La solicitud ACTIVO asociada "
                "todavía no está COMPLETADA"
            )

        prediction = (
            await self._repository
            .get_asset_prediction_by_request(
                request_id=(
                    request.prediction_request_id
                )
            )
        )

        if prediction is None:
            raise AnalysisResultNotFoundError(
                "La solicitud ACTIVO asociada "
                "no tiene una predicción persistida"
            )

        if prediction.activo_id != request.asset_id:
            raise AnalysisRequestInvalidParametersError(
                "La predicción ACTIVO no pertenece "
                "al activo solicitado"
            )

        parameters: dict[str, object] = {
            "asset_id": str(request.asset_id),
            "prediction_request_id": str(
                request.prediction_request_id
            ),
        }

        try:
            analysis_request = (
                await self._repository
                .create_analysis_request(
                    user_id=user_id,
                    analysis_type=(
                        AnalysisType.RECOMMENDATION.value
                    ),
                    horizon=request.horizon.value,
                    reference_date=(
                        request.reference_date
                    ),
                    parameters=parameters,
                    portfolio_id=(
                        request.portfolio_id
                    ),
                )
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise AnalysisRequestPersistenceError(
                "No fue posible registrar "
                "la solicitud de recomendación"
            ) from error

        return AnalysisRequestResponse.model_validate(
            analysis_request
        )

    async def create_integral_request(
        self,
        *,
        user_id: UUID,
        request: IntegralAnalysisRequestCreate,
    ) -> AnalysisRequestResponse:
        prediction_request = (
            await self._repository
            .get_analysis_request_for_user(
                request_id=(
                    request.prediction_request_id
                ),
                user_id=user_id,
            )
        )

        if prediction_request is None:
            raise AnalysisRequestNotFoundError(
                "La solicitud ACTIVO asociada "
                "no existe"
            )

        if (
            prediction_request.tipo_analisis
            != AnalysisType.ASSET.value
        ):
            raise AnalysisRequestInvalidParametersError(
                "prediction_request_id no corresponde "
                "a una solicitud ACTIVO"
            )

        if (
            prediction_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise AnalysisRequestInvalidStateError(
                "La solicitud ACTIVO asociada "
                "todavía no está COMPLETADA"
            )

        prediction = (
            await self._repository
            .get_asset_prediction_by_request(
                request_id=(
                    request.prediction_request_id
                )
            )
        )

        if prediction is None:
            raise AnalysisResultNotFoundError(
                "La solicitud ACTIVO asociada "
                "no tiene una predicción persistida"
            )

        if prediction.activo_id != request.asset_id:
            raise AnalysisRequestInvalidParametersError(
                "La predicción ACTIVO no pertenece "
                "al activo solicitado"
            )

        if (
            len(request.sentiment_request_ids)
            != len(set(request.sentiment_request_ids))
        ):
            raise AnalysisRequestInvalidParametersError(
                "sentiment_request_ids contiene "
                "solicitudes duplicadas"
            )

        for sentiment_request_id in (
            request.sentiment_request_ids
        ):
            sentiment_request = (
                await self._repository
                .get_analysis_request_for_user(
                    request_id=sentiment_request_id,
                    user_id=user_id,
                )
            )

            if sentiment_request is None:
                raise AnalysisRequestNotFoundError(
                    "Una solicitud SENTIMIENTO "
                    "asociada no existe"
                )

            if (
                sentiment_request.tipo_analisis
                != AnalysisType.SENTIMENT.value
            ):
                raise (
                    AnalysisRequestInvalidParametersError(
                        "sentiment_request_ids contiene "
                        "una solicitud que no corresponde "
                        "a SENTIMIENTO"
                    )
                )

            if (
                sentiment_request.estado
                != AnalysisRequestStatus.COMPLETED.value
            ):
                raise AnalysisRequestInvalidStateError(
                    "Una solicitud SENTIMIENTO "
                    "asociada todavía no está COMPLETADA"
                )

            sentiment_analysis = (
                await self._repository
                .get_sentiment_analysis_by_request(
                    request_id=sentiment_request_id
                )
            )

            if sentiment_analysis is None:
                raise AnalysisResultNotFoundError(
                    "Una solicitud SENTIMIENTO "
                    "asociada no tiene un análisis "
                    "persistido"
                )

            if (
                sentiment_analysis.activo_id
                != request.asset_id
            ):
                raise (
                    AnalysisRequestInvalidParametersError(
                        "Un análisis SENTIMIENTO "
                        "no pertenece al activo solicitado"
                    )
                )

        parameters: dict[str, object] = {
            "asset_id": str(request.asset_id),
            "prediction_request_id": str(
                request.prediction_request_id
            ),
            "sentiment_request_ids": [
                str(sentiment_request_id)
                for sentiment_request_id
                in request.sentiment_request_ids
            ],
        }

        try:
            analysis_request = (
                await self._repository
                .create_analysis_request(
                    user_id=user_id,
                    analysis_type=(
                        AnalysisType.INTEGRAL.value
                    ),
                    horizon=request.horizon.value,
                    reference_date=(
                        request.reference_date
                    ),
                    parameters=parameters,
                    portfolio_id=(
                        request.portfolio_id
                    ),
                )
            )

            await self._repository.commit()

        except IntegrityError as error:
            await self._repository.rollback()

            raise AnalysisRequestPersistenceError(
                "No fue posible registrar "
                "la solicitud de análisis integral"
            ) from error

        return AnalysisRequestResponse.model_validate(
            analysis_request
        )

    async def get_user_request(
        self,
        *,
        request_id: UUID,
        user_id: UUID,
    ) -> AnalysisRequestResponse:
        analysis_request = (
            await self._repository
            .get_analysis_request_for_user(
                request_id=request_id,
                user_id=user_id,
            )
        )

        if analysis_request is None:
            raise AnalysisRequestNotFoundError(
                "La solicitud de análisis "
                "no existe"
            )

        return AnalysisRequestResponse.model_validate(
            analysis_request
        )

    async def get_user_result(
        self,
        *,
        request_id: UUID,
        user_id: UUID,
    ) -> AssetAnalysisResultResponse:
        analysis_request = (
            await self._repository
            .get_analysis_request_for_user(
                request_id=request_id,
                user_id=user_id,
            )
        )

        if analysis_request is None:
            raise AnalysisRequestNotFoundError(
                "La solicitud de análisis "
                "no existe"
            )

        if (
            analysis_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise AnalysisResultNotReadyError(
                "La solicitud todavía no tiene "
                "un resultado disponible"
            )

        prediction = (
            await self._repository
            .get_asset_prediction_by_request(
                request_id=request_id
            )
        )

        if prediction is None:
            raise AnalysisResultNotFoundError(
                "La solicitud fue completada pero "
                "no existe una predicción persistida"
            )

        model_output = (
            prediction.salida_modelo
            or {}
        )

        raw_price_version_id = (
            model_output.get(
                "price_forecast_version_id"
            )
        )

        price_version_id: UUID | None = None

        if isinstance(
            raw_price_version_id,
            str,
        ):
            try:
                price_version_id = UUID(
                    raw_price_version_id
                )
            except ValueError:
                price_version_id = None

        bullish = (
            prediction.probabilidad_alcista
        )

        neutral = (
            prediction.probabilidad_neutral
        )

        bearish = (
            prediction.probabilidad_bajista
        )

        if (
            bullish is None
            or neutral is None
            or bearish is None
        ):
            raise AnalysisResultNotFoundError(
                "La predicción persistida no contiene "
                "probabilidades completas"
            )

        raw_horizon = (
            analysis_request.horizonte
        )

        if raw_horizon is None:
            raise AnalysisResultNotFoundError(
                "La solicitud completada no contiene "
                "un horizonte válido"
            )

        horizon = AnalysisHorizon(
            raw_horizon
        )

        return AssetAnalysisResultResponse(
            request_id=prediction.solicitud_id,
            asset_id=prediction.activo_id,
            trend_model_version_id=(
                prediction.version_modelo_id
            ),
            price_forecast_version_id=(
                price_version_id
            ),
            base_date=prediction.fecha_base,
            target_date=prediction.fecha_objetivo,
            horizon=horizon,
            base_price=prediction.precio_base,
            predicted_price=(
                prediction.precio_predicho
            ),
            expected_return_percentage=(
                prediction
                .rendimiento_esperado_porcentaje
            ),
            trend=prediction.tendencia,
            confidence=prediction.confianza,
            probabilities=(
                AssetPredictionProbabilitiesResponse(
                    bullish=bullish,
                    neutral=neutral,
                    bearish=bearish,
                )
            ),
            generated_at=(
                prediction.fecha_generacion
            ),
        )

    async def get_user_recommendation_result(
        self,
        *,
        request_id: UUID,
        user_id: UUID,
    ) -> RecommendationResultResponse:
        analysis_request = (
            await self._repository
            .get_analysis_request_for_user(
                request_id=request_id,
                user_id=user_id,
            )
        )

        if (
            analysis_request is None
            or analysis_request.tipo_analisis
            != AnalysisType.RECOMMENDATION.value
        ):
            raise AnalysisRequestNotFoundError(
                "La solicitud de recomendación "
                "no existe"
            )

        if (
            analysis_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise AnalysisResultNotReadyError(
                "La solicitud todavía no tiene "
                "una recomendación disponible"
            )

        recommendation = (
            await self._repository
            .get_recommendation_by_request(
                request_id=request_id
            )
        )

        if recommendation is None:
            raise AnalysisResultNotFoundError(
                "La solicitud fue completada pero "
                "no existe una recomendación persistida"
            )

        parameters = analysis_request.parametros

        if not isinstance(parameters, dict):
            raise AnalysisResultNotFoundError(
                "La solicitud completada no contiene "
                "parámetros válidos"
            )

        raw_asset_id = parameters.get(
            "asset_id"
        )

        if not isinstance(raw_asset_id, str):
            raise AnalysisResultNotFoundError(
                "La solicitud completada no contiene "
                "un activo válido"
            )

        try:
            asset_id = UUID(raw_asset_id)
        except ValueError as error:
            raise AnalysisResultNotFoundError(
                "La solicitud completada no contiene "
                "un activo válido"
            ) from error

        assets = (
            await self._repository
            .list_recommendation_assets(
                recommendation_id=recommendation.id
            )
        )

        evidence = (
            await self._repository
            .list_analysis_evidence_for_recommendation(
                recommendation_id=recommendation.id
            )
        )

        try:
            horizon = AnalysisHorizon(
                recommendation.horizonte
            )
        except ValueError as error:
            raise AnalysisResultNotFoundError(
                "La recomendación persistida no contiene "
                "un horizonte válido"
            ) from error

        return RecommendationResultResponse(
            request_id=analysis_request.id,
            recommendation_id=(
                recommendation.id
            ),
            user_id=recommendation.usuario_id,
            asset_id=asset_id,
            risk_profile_id=(
                recommendation.perfil_riesgo_id
            ),
            portfolio_id=(
                recommendation.portafolio_id
            ),
            model_version_id=(
                recommendation.version_modelo_id
            ),
            type=recommendation.tipo,
            title=recommendation.titulo,
            summary=recommendation.resumen,
            justification=(
                recommendation.justificacion
            ),
            risk_level=(
                recommendation.nivel_riesgo
            ),
            horizon=horizon,
            confidence=(
                recommendation.confianza
            ),
            priority=recommendation.prioridad,
            status=recommendation.estado,
            warning=recommendation.advertencia,
            parameters=(
                recommendation.parametros
            ),
            generated_at=(
                recommendation.fecha_generacion
            ),
            expires_at=(
                recommendation.fecha_expiracion
            ),
            assets=[
                RecommendationAssetResponse
                .model_validate(item)
                for item in assets
            ],
            evidence=[
                RecommendationEvidenceResponse
                .model_validate(item)
                for item in evidence
            ],
        )

    async def get_user_integral_result(
        self,
        *,
        request_id: UUID,
        user_id: UUID,
    ) -> RecommendationResultResponse:
        analysis_request = (
            await self._repository
            .get_analysis_request_for_user(
                request_id=request_id,
                user_id=user_id,
            )
        )

        if (
            analysis_request is None
            or analysis_request.tipo_analisis
            != AnalysisType.INTEGRAL.value
        ):
            raise AnalysisRequestNotFoundError(
                "La solicitud de análisis integral "
                "no existe"
            )

        if (
            analysis_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise AnalysisResultNotReadyError(
                "La solicitud de análisis integral "
                "todavía no tiene un resultado disponible"
            )

        parameters = analysis_request.parametros

        if not isinstance(
            parameters,
            dict,
        ):
            raise AnalysisResultNotFoundError(
                "La solicitud INTEGRAL completada "
                "no contiene parámetros válidos"
            )

        raw_recommendation_request_id = (
            parameters.get(
                "recommendation_request_id"
            )
        )

        if not isinstance(
            raw_recommendation_request_id,
            str,
        ):
            raise AnalysisResultNotFoundError(
                "La solicitud INTEGRAL completada "
                "no contiene la recomendación asociada"
            )

        try:
            recommendation_request_id = UUID(
                raw_recommendation_request_id
            )

        except ValueError as error:
            raise AnalysisResultNotFoundError(
                "La solicitud INTEGRAL contiene "
                "un identificador de recomendación inválido"
            ) from error

        return await self.get_user_recommendation_result(
            request_id=recommendation_request_id,
            user_id=user_id,
        )

    @staticmethod
    def is_pending(
        response: AnalysisRequestResponse,
    ) -> bool:
        return (
            response.status
            == AnalysisRequestStatus.PENDING
        )



