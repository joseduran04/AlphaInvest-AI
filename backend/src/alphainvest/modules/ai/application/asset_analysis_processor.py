from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.application.asset_analysis_runtime_service import (
    AssetAnalysisRuntimeService,
)
from alphainvest.modules.ai.application.asset_prediction_persistence_service import (
    AssetPredictionPersistenceService,
)
from alphainvest.modules.ai.application.price_forecast_inference_service import (
    PriceForecastInferenceService,
)
from alphainvest.modules.ai.application.trend_inference_service import (
    TrendInferenceService,
)
from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisHorizon,
    AnalysisRequestStatus,
    AnalysisType,
)
from alphainvest.modules.ai.domain.asset_analysis_execution import (
    AssetAnalysisExecutionResult,
)
from alphainvest.modules.ai.domain.exceptions import (
    AnalysisRequestInvalidParametersError,
    AnalysisRequestInvalidStateError,
    AnalysisRequestNotFoundError,
    AnalysisRequestProcessingError,
    AnalysisRequestUnsupportedError,
)
from alphainvest.modules.ai.infrastructure.models import (
    AnalysisRequestModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)


class AssetAnalysisProcessor:
    """Procesa solicitudes ACTIVO mediante PREDICCION_TENDENCIA."""

    FEATURE_START_DATE = date(2000, 1, 1)

    def __init__(
        self,
        *,
        repository: AIRepository,
        inference_service: TrendInferenceService,
        price_forecast_service: (
            PriceForecastInferenceService
            | None
        ) = None,
        runtime_service: (
            AssetAnalysisRuntimeService
            | None
        ) = None,
        market_repository: (
            MarketRepository
            | None
        ) = None,
        prediction_persistence_service: (
            AssetPredictionPersistenceService
            | None
        ) = None,
    ) -> None:
        self._repository = repository

        self._inference_service = (
            inference_service
        )

        self._price_forecast_service = (
            price_forecast_service
        )

        self._runtime_service = runtime_service

        self._market_repository = (
            market_repository
        )

        self._prediction_persistence_service = (
            prediction_persistence_service
        )

    async def process(
        self,
        *,
        request_id: UUID,
        version_id: UUID | None = None,
        price_forecast_version_id: UUID | None = None,
        price_source_id: UUID | None = None,
    ) -> AssetAnalysisExecutionResult:
        analysis_request = (
            await self._repository.get_analysis_request(
                request_id
            )
        )

        if analysis_request is None:
            raise AnalysisRequestNotFoundError(
                "La solicitud de análisis no existe"
            )

        stored_request_id = analysis_request.id

        self._validate_request(
            analysis_request
        )

        horizon = analysis_request.horizonte

        if horizon is None:
            raise ValueError(
                "La solicitud de análisis no tiene horizonte"
            )

        asset_id = self._extract_asset_id(
            analysis_request.parametros
        )

        if version_id is None:
            if self._runtime_service is None:
                raise ValueError(
                    "El resolver runtime del análisis "
                    "no está configurado"
                )

            runtime = (
                await self._runtime_service.resolve()
            )

            version_id = (
                runtime.trend_version_id
            )

            price_forecast_version_id = (
                runtime.price_forecast_version_id
            )

            price_source_id = (
                runtime.price_source_id
            )

        try:
            await self._repository.update_analysis_request_status(
                analysis_request,
                status=AnalysisRequestStatus.RUNNING.value,
                progress=Decimal("10"),
                error_message=None,
            )

            await (
                self._repository
                .increment_analysis_request_attempt(
                    analysis_request
                )
            )

            await self._repository.commit()

            prediction = (
                await self._inference_service.predict_latest(
                    version_id=version_id,
                    asset_id=asset_id,
                    start_date=self.FEATURE_START_DATE,
                    end_date=(
                        analysis_request.fecha_referencia
                    ),
                )
            )

            price_forecast = None

            if price_forecast_version_id is not None:
                if self._price_forecast_service is None:
                    raise ValueError(
                        "El servicio de pronóstico de precio "
                        "no está configurado"
                    )

                if price_source_id is None:
                    raise ValueError(
                        "price_source_id es obligatorio "
                        "para ejecutar PRONOSTICO_PRECIO"
                    )

                price_forecast = (
                    await self._price_forecast_service
                    .predict_latest(
                        version_id=(
                            price_forecast_version_id
                        ),
                        asset_id=asset_id,
                        source_id=price_source_id,
                    )
                )

            if price_forecast is not None:
                if self._market_repository is None:
                    raise ValueError(
                        "El repositorio de mercado "
                        "no está configurado"
                    )

                if (
                    self._prediction_persistence_service
                    is None
                ):
                    raise ValueError(
                        "El servicio de persistencia "
                        "de predicciones no está configurado"
                    )

                asset = (
                    await self._market_repository.get_asset(
                        asset_id
                    )
                )

                if asset is None:
                    raise ValueError(
                        "El activo asociado con la solicitud "
                        "no existe"
                    )

                market_code = asset.mercado.codigo

                execution_result = (
                    AssetAnalysisExecutionResult(
                        request_id=analysis_request.id,
                        prediction=prediction,
                        price_forecast=price_forecast,
                    )
                )

                await (
                    self._prediction_persistence_service
                    .persist(
                        request_id=analysis_request.id,
                        asset_id=asset_id,
                        market_code=market_code,
                        horizon=horizon,
                        result=execution_result,
                    )
                )

            await self._repository.update_analysis_request_status(
                analysis_request,
                status=AnalysisRequestStatus.COMPLETED.value,
                progress=Decimal("100"),
                error_message=None,
            )

            await self._repository.commit()

        except Exception as error:
            await self._repository.rollback()

            await self._mark_failed(
                request_id=stored_request_id,
                error=error,
            )

            raise AnalysisRequestProcessingError(
                "No fue posible procesar "
                "la solicitud de análisis"
            ) from error

        return AssetAnalysisExecutionResult(
            request_id=analysis_request.id,
            prediction=prediction,
            price_forecast=price_forecast,
        )

    @staticmethod
    def _validate_request(
        analysis_request: AnalysisRequestModel,
    ) -> None:
        analysis_type = getattr(
            analysis_request,
            "tipo_analisis",
            None,
        )

        if analysis_type != AnalysisType.ASSET.value:
            raise AnalysisRequestUnsupportedError(
                "El procesador sólo admite "
                "solicitudes de tipo ACTIVO"
            )

        horizon = getattr(
            analysis_request,
            "horizonte",
            None,
        )

        if horizon != AnalysisHorizon.SHORT_TERM.value:
            raise AnalysisRequestUnsupportedError(
                "PREDICCION_TENDENCIA 0.1.0 "
                "sólo soporta CORTO_PLAZO"
            )

        request_status = getattr(
            analysis_request,
            "estado",
            None,
        )

        if request_status != AnalysisRequestStatus.PENDING.value:
            raise AnalysisRequestInvalidStateError(
                "La solicitud debe estar PENDIENTE "
                "antes de ser procesada"
            )

    @staticmethod
    def _extract_asset_id(
        parameters: dict[str, object] | None,
    ) -> UUID:
        if parameters is None:
            raise AnalysisRequestInvalidParametersError(
                "La solicitud no contiene parámetros"
            )

        raw_asset_id = parameters.get(
            "asset_id"
        )

        if not isinstance(raw_asset_id, str):
            raise AnalysisRequestInvalidParametersError(
                "La solicitud no contiene un asset_id válido"
            )

        try:
            return UUID(raw_asset_id)

        except ValueError as error:
            raise AnalysisRequestInvalidParametersError(
                "El asset_id de la solicitud "
                "no tiene formato UUID"
            ) from error

    async def _mark_failed(
        self,
        *,
        request_id: UUID,
        error: Exception,
    ) -> None:
        error_message = str(error).strip()

        if not error_message:
            error_message = (
                "Error no especificado durante "
                "el análisis"
            )

        try:
            analysis_request = (
                await self._repository.get_analysis_request(
                    request_id
                )
            )

            if analysis_request is None:
                return

            await self._repository.update_analysis_request_status(
                analysis_request,
                status=AnalysisRequestStatus.FAILED.value,
                progress=None,
                error_message=error_message[:2000],
            )

            await self._repository.commit()

        except Exception:
            await self._repository.rollback()
