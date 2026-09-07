import logging
from uuid import uuid4

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)
from alphainvest.modules.ai.application.asset_analysis_processor import (
    AssetAnalysisProcessor,
)
from alphainvest.modules.ai.application.asset_analysis_runtime_service import (
    AssetAnalysisRuntimeService,
)
from alphainvest.modules.ai.application.asset_prediction_persistence_service import (
    AssetPredictionPersistenceService,
)
from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.price_forecast_inference_service import (
    PriceForecastInferenceService,
)
from alphainvest.modules.ai.application.price_forecast_model_runtime_service import (
    PriceForecastModelRuntimeService,
)
from alphainvest.modules.ai.application.trend_inference_service import (
    TrendInferenceService,
)
from alphainvest.modules.ai.application.trend_model_runtime_service import (
    TrendModelRuntimeService,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.application.service import (
    MarketService,
)
from alphainvest.modules.market.infrastructure.exchange_trading_calendar import (
    ExchangeTradingCalendar,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

logger = logging.getLogger(__name__)


JOB_CODE = "PROCESAR_ANALISIS_ACTIVOS_PENDIENTES"

ANALYSIS_LOCK_PREFIX = "AI_ANALYSIS_REQUEST"
ANALYSIS_LOCK_OWNER = "alphainvest-worker"




async def process_pending_asset_analysis_requests(
    settings: Settings,
) -> None:
    """Procesa solicitudes ACTIVO pendientes."""


    async with AsyncSessionFactory() as session:
        repository = AIRepository(session)

        operation_repository = (
            OperationRepository(session)
        )

        job = await operation_repository.get_job_by_code(
            JOB_CODE
        )

        if job is None:
            raise RuntimeError(
                "No existe la configuración activa "
                f"del trabajo {JOB_CODE}"
            )

        max_attempts = (
            1
            + job.maximo_reintentos
        )

        expired_locks = (
            await operation_repository
            .mark_expired_process_locks()
        )

        if expired_locks:
            logger.info(
                "Se marcaron %s bloqueo(s) expirado(s)",
                expired_locks,
            )

        running_requests = (
            await repository
            .list_running_asset_analysis_requests(
                limit=(
                    settings
                    .worker_ai_analysis_batch_size
                )
            )
        )

        recovered = 0
        permanently_failed = 0

        for running_request in running_requests:
            lock_key = (
                f"{ANALYSIS_LOCK_PREFIX}:"
                f"{running_request.id}"
            )

            lock_active = (
                await operation_repository
                .is_process_lock_active(
                    lock_key=lock_key
                )
            )

            if lock_active:
                continue

            if (
                running_request
                .intentos_procesamiento
                >= max_attempts
            ):
                await (
                    repository
                    .update_analysis_request_status(
                        running_request,
                        status="FALLIDA",
                        progress=(
                            running_request
                            .porcentaje_progreso
                        ),
                        error_message=(
                            "La solicitud agotó el máximo "
                            "de intentos tras detectar "
                            "ejecuciones huérfanas"
                        ),
                    )
                )

                permanently_failed += 1

                continue

            await (
                repository
                .reset_analysis_request_for_retry(
                    running_request
                )
            )

            recovered += 1

        await operation_repository.commit()

        if recovered:
            logger.warning(
                (
                    "Se recuperaron %s solicitud(es) "
                    "ACTIVO huérfanas"
                ),
                recovered,
            )

        if permanently_failed:
            logger.error(
                (
                    "%s solicitud(es) agotaron "
                    "sus intentos"
                ),
                permanently_failed,
            )

        pending_requests = (
            await repository
            .list_pending_asset_analysis_requests(
                limit=(
                    settings
                    .worker_ai_analysis_batch_size
                )
            )
        )

    if not pending_requests:
        logger.info(
            "No existen análisis ACTIVO pendientes"
        )
        return

    logger.info(
        "Se encontraron %s análisis ACTIVO pendientes",
        len(pending_requests),
    )

    for analysis_request in pending_requests:
        async with AsyncSessionFactory() as session:
            ai_repository = AIRepository(session)

            market_repository = MarketRepository(
                session
            )

            operation_repository = (
                OperationRepository(session)
            )

            trend_runtime_service = (
                TrendModelRuntimeService(
                    ai_repository
                )
            )

            feature_service = (
                AIFeatureDataService(
                    market_repository=(
                        market_repository
                    ),
                    source_name=(
                        settings
                        .worker_ai_analysis_source_name
                    ),
                )
            )

            trend_inference_service = (
                TrendInferenceService(
                    runtime_service=(
                        trend_runtime_service
                    ),
                    feature_service=feature_service,
                )
            )

            price_runtime_service = (
                PriceForecastModelRuntimeService(
                    ai_repository
                )
            )

            market_service = MarketService(
                market_repository
            )

            price_forecast_service = (
                PriceForecastInferenceService(
                    runtime_service=(
                        price_runtime_service
                    ),
                    market_service=market_service,
                )
            )

            asset_runtime_service = (
                AssetAnalysisRuntimeService(
                    ai_repository=ai_repository,
                    market_repository=(
                        market_repository
                    ),
                )
            )

            trading_calendar = (
                ExchangeTradingCalendar()
            )

            prediction_persistence_service = (
                AssetPredictionPersistenceService(
                    repository=ai_repository,
                    trading_calendar=(
                        trading_calendar
                    ),
                )
            )

            processor = AssetAnalysisProcessor(
                repository=ai_repository,
                inference_service=(
                    trend_inference_service
                ),
                price_forecast_service=(
                    price_forecast_service
                ),
                runtime_service=(
                    asset_runtime_service
                ),
                market_repository=(
                    market_repository
                ),
                prediction_persistence_service=(
                    prediction_persistence_service
                ),
            )

            process_id = (
                f"AI_ANALYSIS_"
                f"{analysis_request.id}_"
                f"{uuid4().hex}"
            )

            lock_key = (
                f"{ANALYSIS_LOCK_PREFIX}:"
                f"{analysis_request.id}"
            )

            lock_acquired = False

            try:
                lock_acquired = (
                    await operation_repository
                    .acquire_process_lock(
                        process_type="ANALISIS_IA",
                        lock_key=lock_key,
                        owner=ANALYSIS_LOCK_OWNER,
                        process_id=process_id,
                        duration_seconds=(
                            settings
                            .worker_ai_analysis_lock_seconds
                        ),
                        entity_type=(
                            "SOLICITUD_ANALISIS"
                        ),
                        entity_id=str(
                            analysis_request.id
                        ),
                        metadata={
                            "request_id": str(
                                analysis_request.id
                            ),
                            "job": JOB_CODE,
                        },
                    )
                )

                if not lock_acquired:
                    await (
                        operation_repository
                        .rollback()
                    )

                    logger.info(
                        (
                            "La solicitud de análisis "
                            "ya está siendo procesada: "
                            "request_id=%s"
                        ),
                        analysis_request.id,
                    )

                    continue

                await operation_repository.commit()

                current_request = (
                    await ai_repository
                    .get_analysis_request(
                        analysis_request.id
                    )
                )

                if (
                    current_request is None
                    or current_request.estado
                    != "PENDIENTE"
                ):
                    await (
                        operation_repository
                        .release_process_lock(
                            lock_key=lock_key,
                            process_id=process_id,
                        )
                    )

                    await operation_repository.commit()

                    lock_acquired = False

                    logger.info(
                        (
                            "Solicitud omitida porque "
                            "ya no está PENDIENTE: "
                            "request_id=%s"
                        ),
                        analysis_request.id,
                    )

                    continue

                if (
                    current_request.intentos_procesamiento
                    >= max_attempts
                ):
                    await (
                        ai_repository
                        .update_analysis_request_status(
                            current_request,
                            status="FALLIDA",
                            progress=(
                                current_request
                                .porcentaje_progreso
                            ),
                            error_message=(
                                "La solicitud agotó el máximo "
                                "de intentos permitidos"
                            ),
                        )
                    )

                    await (
                        operation_repository
                        .release_process_lock(
                            lock_key=lock_key,
                            process_id=process_id,
                        )
                    )

                    await operation_repository.commit()

                    lock_acquired = False

                    logger.error(
                        (
                            "Solicitud agotada sin procesar: "
                            "request_id=%s intentos=%s"
                        ),
                        current_request.id,
                        current_request.intentos_procesamiento,
                    )

                    continue

                await processor.process(
                    request_id=analysis_request.id
                )

                await (
                    operation_repository
                    .release_process_lock(
                        lock_key=lock_key,
                        process_id=process_id,
                    )
                )

                await operation_repository.commit()

                lock_acquired = False

                logger.info(
                    (
                        "Análisis ACTIVO completado: "
                        "request_id=%s"
                    ),
                    analysis_request.id,
                )

            except Exception:
                await operation_repository.rollback()

                if lock_acquired:
                    try:
                        await (
                            operation_repository
                            .release_process_lock(
                                lock_key=lock_key,
                                process_id=process_id,
                            )
                        )

                        await (
                            operation_repository.commit()
                        )

                    except Exception:
                        await (
                            operation_repository
                            .rollback()
                        )

                        logger.exception(
                            (
                                "No fue posible liberar "
                                "el bloqueo de análisis "
                                "request_id=%s"
                            ),
                            analysis_request.id,
                        )

                logger.exception(
                    (
                        "Falló el procesamiento de "
                        "análisis request_id=%s"
                    ),
                    analysis_request.id,
                )