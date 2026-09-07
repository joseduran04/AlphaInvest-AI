import logging
from uuid import UUID, uuid4

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)
from alphainvest.modules.ai.application.integral_analysis_processor import (
    IntegralAnalysisProcessor,
)
from alphainvest.modules.ai.application.recommendation_context_builder import (
    RecommendationContextBuilder,
)
from alphainvest.modules.ai.application.recommendation_processor import (
    RecommendationProcessor,
)
from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisRequestStatus,
)
from alphainvest.modules.ai.domain.recommendation_engine import (
    RecommendationEngine,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.operation.application.notification_service import (
    NotificationService,
)
from alphainvest.modules.operation.domain.enums import (
    NotificationType,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)
from alphainvest.modules.portfolio.infrastructure.repository import (
    PortfolioRepository,
)
from alphainvest.modules.profile.infrastructure.repository import (
    ProfileRepository,
)

logger = logging.getLogger(__name__)


JOB_CODE = (
    "PROCESAR_ANALISIS_INTEGRALES_PENDIENTES"
)

ANALYSIS_LOCK_PREFIX = (
    "AI_INTEGRAL_ANALYSIS_REQUEST"
)

ANALYSIS_LOCK_OWNER = "alphainvest-worker"


async def process_pending_integral_analysis_requests(
    settings: Settings,
) -> None:
    """Procesa solicitudes INTEGRAL pendientes."""

    async with AsyncSessionFactory() as session:
        ai_repository = AIRepository(
            session
        )

        operation_repository = (
            OperationRepository(
                session
            )
        )

        job = (
            await operation_repository
            .get_job_by_code(
                JOB_CODE
            )
        )

        if job is None:
            raise RuntimeError(
                "No existe la configuración "
                f"activa del trabajo {JOB_CODE}"
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
                (
                    "Se marcaron %s bloqueo(s) "
                    "expirado(s)"
                ),
                expired_locks,
            )

        running_requests = (
            await ai_repository
            .list_running_integral_analysis_requests(
                limit=(
                    settings
                    .worker_ai_analysis_batch_size
                )
            )
        )

        recovered = 0
        permanently_failed = 0

        for request in running_requests:
            lock_key = (
                f"{ANALYSIS_LOCK_PREFIX}:"
                f"{request.id}"
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
                request.intentos_procesamiento
                >= max_attempts
            ):
                await (
                    ai_repository
                    .update_analysis_request_status(
                        request,
                        status=(
                            AnalysisRequestStatus
                            .FAILED
                            .value
                        ),
                        progress=(
                            request
                            .porcentaje_progreso
                        ),
                        error_message=(
                            "La solicitud agotó "
                            "el máximo de intentos "
                            "tras detectar una "
                            "ejecución huérfana"
                        ),
                    )
                )

                permanently_failed += 1
                continue

            await (
                ai_repository
                .reset_analysis_request_for_retry(
                    request
                )
            )

            recovered += 1

        await ai_repository.commit()

        if recovered:
            logger.warning(
                (
                    "Se recuperaron %s "
                    "solicitud(es) INTEGRAL "
                    "huérfanas"
                ),
                recovered,
            )

        if permanently_failed:
            logger.error(
                (
                    "%s solicitud(es) "
                    "INTEGRAL agotaron "
                    "sus intentos"
                ),
                permanently_failed,
            )

        pending_requests = (
            await ai_repository
            .list_pending_integral_analysis_requests(
                limit=(
                    settings
                    .worker_ai_analysis_batch_size
                )
            )
        )

    if not pending_requests:
        logger.info(
            "No existen análisis "
            "INTEGRAL pendientes"
        )
        return

    logger.info(
        (
            "Se encontraron %s análisis "
            "INTEGRAL pendientes"
        ),
        len(pending_requests),
    )

    for analysis_request in pending_requests:
        await _process_request(
            settings=settings,
            analysis_request_id=(
                analysis_request.id
            ),
            max_attempts=max_attempts,
        )


async def _process_request(
    *,
    settings: Settings,
    analysis_request_id: UUID,
    max_attempts: int,
) -> None:
    async with AsyncSessionFactory() as session:
        ai_repository = AIRepository(
            session
        )

        market_repository = MarketRepository(
            session
        )

        profile_repository = ProfileRepository(
            session
        )

        portfolio_repository = (
            PortfolioRepository(
                session
            )
        )

        operation_repository = (
            OperationRepository(
                session
            )
        )

        notification_service = (
            NotificationService(
                operation_repository
            )
        )

        context_builder = (
            RecommendationContextBuilder(
                ai_repository=ai_repository,
                market_repository=(
                    market_repository
                ),
                profile_repository=(
                    profile_repository
                ),
                portfolio_repository=(
                    portfolio_repository
                ),
            )
        )

        recommendation_engine = (
            RecommendationEngine()
        )

        recommendation_processor = (
            RecommendationProcessor(
                ai_repository=ai_repository,
                context_builder=context_builder,
                engine=(
                    recommendation_engine
                ),
            )
        )

        processor = IntegralAnalysisProcessor(
            ai_repository=ai_repository,
            recommendation_processor=(
                recommendation_processor
            ),
        )

        process_id = (
            "AI_INTEGRAL_"
            f"{analysis_request_id}_"
            f"{uuid4().hex}"
        )

        lock_key = (
            f"{ANALYSIS_LOCK_PREFIX}:"
            f"{analysis_request_id}"
        )

        lock_acquired = False

        try:
            lock_acquired = (
                await operation_repository
                .acquire_process_lock(
                    process_type=(
                        "ANALISIS_IA"
                    ),
                    lock_key=lock_key,
                    owner=(
                        ANALYSIS_LOCK_OWNER
                    ),
                    process_id=process_id,
                    duration_seconds=(
                        settings
                        .worker_ai_analysis_lock_seconds
                    ),
                    entity_type=(
                        "SOLICITUD_ANALISIS"
                    ),
                    entity_id=str(
                        analysis_request_id
                    ),
                    metadata={
                        "request_id": str(
                            analysis_request_id
                        ),
                        "job": JOB_CODE,
                        "analysis_type": (
                            "INTEGRAL"
                        ),
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
                        "Solicitud INTEGRAL "
                        "ya en procesamiento: "
                        "request_id=%s"
                    ),
                    analysis_request_id,
                )

                return

            await operation_repository.commit()

            current_request = (
                await ai_repository
                .get_analysis_request(
                    analysis_request_id
                )
            )

            if (
                current_request is None
                or current_request.estado
                != AnalysisRequestStatus.PENDING.value
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
                return

            if (
                current_request
                .intentos_procesamiento
                >= max_attempts
            ):
                await (
                    ai_repository
                    .update_analysis_request_status(
                        current_request,
                        status=(
                            AnalysisRequestStatus
                            .FAILED
                            .value
                        ),
                        progress=(
                            current_request
                            .porcentaje_progreso
                        ),
                        error_message=(
                            "La solicitud agotó "
                            "el máximo de intentos "
                            "permitidos"
                        ),
                    )
                )

                await ai_repository.commit()

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
                        "Solicitud INTEGRAL "
                        "agotada: request_id=%s"
                    ),
                    analysis_request_id,
                )

                return

            await processor.process(
                request_id=analysis_request_id
            )

            try:
                await (
                    notification_service
                    .create_application_notification_once(
                        user_id=(
                            current_request
                            .usuario_id
                        ),
                        notification_type=(
                            NotificationType
                            .AI_ANALYSIS
                        ),
                        title=(
                            "Análisis integral "
                            "completado"
                        ),
                        message=(
                            "Tu análisis integral "
                            "finalizó correctamente "
                            "y sus resultados ya "
                            "están disponibles."
                        ),
                        data={
                            "request_id": str(
                                analysis_request_id
                            ),
                            "analysis_type": (
                                "INTEGRAL"
                            ),
                        },
                        reference_type=(
                            "ANALISIS_INTEGRAL"
                        ),
                        reference_id=str(
                            analysis_request_id
                        ),
                    )
                )

            except Exception:
                await (
                    operation_repository
                    .rollback()
                )

                logger.exception(
                    (
                        "No fue posible generar "
                        "la notificación del "
                        "análisis INTEGRAL: "
                        "request_id=%s"
                    ),
                    analysis_request_id,
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
                    "Análisis INTEGRAL "
                    "completado: request_id=%s"
                ),
                analysis_request_id,
            )

        except Exception as error:
            await ai_repository.rollback()
            await operation_repository.rollback()

            await _handle_processing_failure(
                analysis_request_id=(
                    analysis_request_id
                ),
                max_attempts=max_attempts,
                error=error,
            )

            if lock_acquired:
                try:
                    await (
                        operation_repository
                        .release_process_lock(
                            lock_key=lock_key,
                            process_id=process_id,
                        )
                    )

                    await operation_repository.commit()

                except Exception:
                    await (
                        operation_repository
                        .rollback()
                    )

                    logger.exception(
                        (
                            "No fue posible liberar "
                            "el bloqueo INTEGRAL "
                            "request_id=%s"
                        ),
                        analysis_request_id,
                    )

            logger.exception(
                (
                    "Falló procesamiento "
                    "INTEGRAL request_id=%s"
                ),
                analysis_request_id,
            )


async def _handle_processing_failure(
    *,
    analysis_request_id: UUID,
    max_attempts: int,
    error: Exception,
) -> None:
    async with AsyncSessionFactory() as session:
        repository = AIRepository(
            session
        )

        request = (
            await repository
            .get_analysis_request(
                analysis_request_id
            )
        )

        if request is None:
            return

        if (
            request.intentos_procesamiento
            >= max_attempts
        ):
            await (
                repository
                .update_analysis_request_status(
                    request,
                    status=(
                        AnalysisRequestStatus
                        .FAILED
                        .value
                    ),
                    progress=(
                        request
                        .porcentaje_progreso
                    ),
                    error_message=str(
                        error
                    )[:1000],
                )
            )

        else:
            await (
                repository
                .reset_analysis_request_for_retry(
                    request
                )
            )

        await repository.commit()