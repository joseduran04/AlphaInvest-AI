import logging
from uuid import UUID, uuid4

from alphainvest.core.config import Settings
from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)
from alphainvest.modules.market.application.indicator_service import (
    FinancialIndicatorService,
)
from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.market.presentation.schemas import (
    IndicatorCalculationRequest,
    IndicatorCalculationSpec,
)
from alphainvest.modules.operation.domain.enums import (
    JobTrigger,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

logger = logging.getLogger(__name__)

INDICATOR_JOB_CODE = "CALCULAR_INDICADORES_DIARIOS"
INDICATOR_SOURCE_NAME = "Alpha Vantage"
INDICATOR_LOCK_PREFIX = "MARKET_INDICATORS"
INDICATOR_LOCK_OWNER = "alphainvest-worker"
INDICATOR_LOCK_DURATION_SECONDS = 900


def build_daily_indicator_request(
    *,
    source_id: UUID,
) -> IndicatorCalculationRequest:
    """Configuración estándar de indicadores diarios."""

    return IndicatorCalculationRequest(
        source_id=source_id,
        calculations=[
            IndicatorCalculationSpec(
                indicator_type=FinancialIndicatorType.SMA,
                period=20,
            ),
            IndicatorCalculationSpec(
                indicator_type=FinancialIndicatorType.EMA,
                period=20,
            ),
            IndicatorCalculationSpec(
                indicator_type=FinancialIndicatorType.RSI,
                period=14,
            ),
            IndicatorCalculationSpec(
                indicator_type=(
                    FinancialIndicatorType.VOLATILITY
                ),
                period=30,
            ),
            IndicatorCalculationSpec(
                indicator_type=FinancialIndicatorType.MACD,
                fast_period=12,
                slow_period=26,
                signal_period=9,
            ),
        ],
    )


async def calculate_configured_market_indicators(
    settings: Settings,
) -> None:
    """Calcula indicadores para los símbolos configurados."""

    symbols = settings.worker_price_symbols

    if not symbols:
        logger.warning(
            "El worker no tiene símbolos configurados"
        )
        return

    for symbol in symbols:
        async with AsyncSessionFactory() as session:
            market_repository = MarketRepository(session)
            operation_repository = OperationRepository(session)

            execution_id = None
            lock_acquired = False

            asset = (
                await market_repository
                .get_active_asset_by_symbol(symbol)
            )

            if asset is None:
                logger.warning(
                    "No existe un activo activo para %s",
                    symbol,
                )
                continue

            source = (
                await market_repository
                .get_financial_source_by_name(
                    name=INDICATOR_SOURCE_NAME,
                    active_only=True,
                )
            )

            if source is None:
                logger.warning(
                    "No existe la fuente activa %s",
                    INDICATOR_SOURCE_NAME,
                )
                continue

            job = await operation_repository.get_job_by_code(
                INDICATOR_JOB_CODE
            )

            if job is None:
                logger.warning(
                    "No existe el trabajo %s",
                    INDICATOR_JOB_CODE,
                )
                continue

            process_id = (
                f"INDICATORS_{asset.id}_{uuid4().hex}"
            )
            lock_key = (
                f"{INDICATOR_LOCK_PREFIX}:{asset.id}"
            )

            try:
                lock_acquired = (
                    await operation_repository
                    .acquire_process_lock(
                        process_type="TRABAJO_PROGRAMADO",
                        lock_key=lock_key,
                        owner=INDICATOR_LOCK_OWNER,
                        process_id=process_id,
                        duration_seconds=(
                            INDICATOR_LOCK_DURATION_SECONDS
                        ),
                        entity_type="ACTIVO",
                        entity_id=str(asset.id),
                        metadata={
                            "asset_id": str(asset.id),
                            "symbol": asset.simbolo,
                            "source_id": str(source.id),
                            "source_name": source.nombre,
                        },
                    )
                )

                if not lock_acquired:
                    await operation_repository.rollback()

                    logger.info(
                        (
                            "Los indicadores de %s ya están "
                            "siendo calculados"
                        ),
                        symbol,
                    )
                    continue

                execution = (
                    await operation_repository.create_execution(
                        job_id=job.id,
                        requested_by=None,
                        process_id=process_id,
                        trigger=JobTrigger.SCHEDULED,
                    )
                )
                execution_id = execution.id

                await operation_repository.commit()

                indicator_service = (
                    FinancialIndicatorService(
                        market_repository
                    )
                )

                request = build_daily_indicator_request(
                    source_id=source.id
                )

                result = (
                    await indicator_service
                    .calculate_indicators(
                        asset_id=asset.id,
                        request=request,
                    )
                )

                current_execution = (
                    await operation_repository.get_execution(
                        execution.id
                    )
                )

                if current_execution is None:
                    raise RuntimeError(
                        "No fue posible recuperar la ejecución"
                    )

                result_data = {
                    "asset_id": str(result.asset_id),
                    "symbol": result.symbol,
                    "source_id": str(result.source_id),
                    "source_name": result.source_name,
                    "total_calculated": (
                        result.total_calculated
                    ),
                    "total_created": result.total_created,
                    "total_updated": result.total_updated,
                    "items": [
                        {
                            "indicator_type": (
                                item.indicator_type.value
                            ),
                            "period": item.period,
                            "calculated": item.calculated,
                            "created": item.created,
                            "updated": item.updated,
                        }
                        for item in result.items
                    ],
                }

                await operation_repository.mark_completed(
                    current_execution,
                    processed=result.total_calculated,
                    successful=result.total_calculated,
                    failed=0,
                    result=result_data,
                )

                await operation_repository.update_job_last_execution(
                    job
                )

                await operation_repository.release_process_lock(
                    lock_key=lock_key,
                    process_id=process_id,
                )

                await operation_repository.commit()

                logger.info(
                    (
                        "Indicadores completados: "
                        "symbol=%s execution_id=%s "
                        "calculated=%s created=%s updated=%s"
                    ),
                    result.symbol,
                    execution.id,
                    result.total_calculated,
                    result.total_created,
                    result.total_updated,
                )

            except Exception as error:
                await operation_repository.rollback()

                if execution_id is not None:
                    current_execution = (
                        await operation_repository
                        .get_execution(execution_id)
                    )

                    if current_execution is not None:
                        await operation_repository.mark_failed(
                            current_execution,
                            message=str(error)[:2000],
                        )

                if lock_acquired:
                    await operation_repository.release_process_lock(
                        lock_key=lock_key,
                        process_id=process_id,
                    )

                await operation_repository.commit()

                logger.exception(
                    "Falló el cálculo de indicadores de %s",
                    symbol,
                )

                raise