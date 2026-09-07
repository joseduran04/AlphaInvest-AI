import logging
from uuid import uuid4

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
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
from alphainvest.modules.simulation.application.execution_processor import (
    HistoricalExecutionProcessor,
)
from alphainvest.modules.simulation.application.historical_data_service import (
    HistoricalDataService,
)
from alphainvest.modules.simulation.infrastructure.repository import (
    SimulationRepository,
)

logger = logging.getLogger(__name__)

SIMULATION_LOCK_PREFIX = "SIMULATION_EXECUTION"
SIMULATION_LOCK_OWNER = "alphainvest-worker"
SIMULATION_LOCK_DURATION_SECONDS = 1800


async def process_pending_simulation_executions(
    settings: Settings,
) -> None:
    """Procesa ejecuciones históricas pendientes."""

    async with AsyncSessionFactory() as session:
        simulation_repository = (
            SimulationRepository(session)
        )

        pending_executions = (
            await simulation_repository
            .list_pending_executions_for_processing(
                limit=(
                    settings
                    .worker_simulation_batch_size
                )
            )
        )

    if not pending_executions:
        logger.info(
            "No existen simulaciones pendientes"
        )
        return

    logger.info(
        "Se encontraron %s simulación(es) pendientes",
        len(pending_executions),
    )

    for execution in pending_executions:
        async with AsyncSessionFactory() as session:
            simulation_repository = (
                SimulationRepository(session)
            )

            market_repository = MarketRepository(
                session
            )

            operation_repository = (
                OperationRepository(session)
            )

            notification_service = (
                NotificationService(
                    operation_repository
                )
            )

            historical_data_service = (
                HistoricalDataService(
                    market_repository=(
                        market_repository
                    ),
                    source_name=(
                        settings
                        .worker_simulation_source_name
                    ),
                )
            )

            processor = HistoricalExecutionProcessor(
                repository=simulation_repository,
                historical_data_service=(
                    historical_data_service
                ),
            )

            process_id = (
                f"SIMULATION_{execution.id}_"
                f"{uuid4().hex}"
            )

            lock_key = (
                f"{SIMULATION_LOCK_PREFIX}:"
                f"{execution.id}"
            )

            lock_acquired = False

            try:
                lock_acquired = (
                    await operation_repository
                    .acquire_process_lock(
                        process_type="SIMULACION",
                        lock_key=lock_key,
                        owner=SIMULATION_LOCK_OWNER,
                        process_id=process_id,
                        duration_seconds=(
                            SIMULATION_LOCK_DURATION_SECONDS
                        ),
                        entity_type=(
                            "EJECUCION_SIMULACION"
                        ),
                        entity_id=str(execution.id),
                        metadata={
                            "execution_id": str(
                                execution.id
                            ),
                            "job": (
                                "PROCESAR_"
                                "SIMULACIONES_PENDIENTES"
                            ),
                        },
                    )
                )

                if not lock_acquired:
                    await operation_repository.rollback()

                    logger.info(
                        (
                            "La simulación ya está siendo "
                            "procesada: execution_id=%s"
                        ),
                        execution.id,
                    )
                    continue

                await operation_repository.commit()

                await processor.process(
                    execution_id=execution.id
                )

                try:
                    await (
                        notification_service
                        .create_application_notification_once(
                            user_id=(
                                execution.usuario_id
                            ),
                            notification_type=(
                                NotificationType
                                .SIMULATION
                            ),
                            title=(
                                "Simulación completada"
                            ),
                            message=(
                                "Tu simulación histórica "
                                "finalizó correctamente "
                                "y sus resultados ya están "
                                "disponibles para consulta."
                            ),
                            data={
                                "execution_id": str(
                                    execution.id
                                ),
                                "configuration_id": str(
                                    execution
                                    .configuracion_id
                                ),
                            },
                            reference_type=(
                                "EJECUCION_SIMULACION"
                            ),
                            reference_id=str(
                                execution.id
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
                            "la notificación de la "
                            "simulación: "
                            "execution_id=%s"
                        ),
                        execution.id,
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
                        "Simulación completada: "
                        "execution_id=%s"
                    ),
                    execution.id,
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

                        await operation_repository.commit()

                    except Exception:
                        await operation_repository.rollback()

                        logger.exception(
                            (
                                "No fue posible liberar el "
                                "bloqueo de simulation "
                                "execution_id=%s"
                            ),
                            execution.id,
                        )

                logger.exception(
                    (
                        "Falló el procesamiento de "
                        "simulation execution_id=%s"
                    ),
                    execution.id,
                )