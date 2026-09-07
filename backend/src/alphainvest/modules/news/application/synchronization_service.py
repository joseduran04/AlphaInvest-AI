from datetime import UTC, datetime
from uuid import UUID, uuid4

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    ProcessLockUnavailableError,
    ScheduledJobNotFoundError,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.news.domain.exceptions import (
    NewsPersistenceError,
    NewsSynchronizationError,
)
from alphainvest.modules.news.domain.provider import (
    NewsProvider,
)
from alphainvest.modules.news.domain.storage import (
    NewsAssetStorage,
)
from alphainvest.modules.news.presentation.schemas import (
    NewsSynchronizationResponse,
)
from alphainvest.modules.operation.domain.enums import (
    JobTrigger,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

NEWS_SYNC_JOB_CODE = "SINCRONIZAR_NOTICIAS"

NEWS_SYNC_LOCK_PREFIX = "NEWS_SYNC"

NEWS_SYNC_LOCK_OWNER = "alphainvest-api"

NEWS_SYNC_DEFAULT_LOCK_SECONDS = 1200


class NewsSynchronizationService:
    """Sincroniza noticias externas con control operativo."""

    def __init__(
        self,
        *,
        market_repository: MarketRepository,
        operation_repository: OperationRepository,
        provider: NewsProvider,
        storage: NewsAssetStorage,
    ) -> None:
        self._market_repository = (
            market_repository
        )
        self._operation_repository = (
            operation_repository
        )
        self._provider = provider
        self._storage = storage

    async def synchronize_asset(
        self,
        *,
        asset_id: UUID,
        requested_by: UUID | None,
        start_at: datetime | None,
        end_at: datetime | None,
        limit: int,
        trigger: JobTrigger = JobTrigger.MANUAL,
    ) -> NewsSynchronizationResponse:
        if (
            start_at is not None
            and end_at is not None
            and start_at > end_at
        ):
            raise ValueError(
                "La fecha inicial no puede ser "
                "posterior a la fecha final"
            )

        asset = (
            await self._market_repository
            .get_asset(asset_id)
        )

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        source = (
            await self._market_repository
            .get_financial_source_by_name(
                name=self._provider.source_name,
                active_only=True,
            )
        )

        if source is None:
            raise FinancialSourceNotFoundError(
                "No existe una fuente financiera "
                "activa llamada "
                f"{self._provider.source_name}"
            )

        job = (
            await self._operation_repository
            .get_job_by_code(
                NEWS_SYNC_JOB_CODE
            )
        )

        if job is None:
            raise ScheduledJobNotFoundError(
                "No existe el trabajo operativo "
                "SINCRONIZAR_NOTICIAS"
            )

        process_id = (
            f"NEWS_SYNC_{asset.id}_"
            f"{uuid4().hex}"
        )

        lock_key = (
            f"{NEWS_SYNC_LOCK_PREFIX}:"
            f"{asset.id}"
        )

        lock_seconds = (
            job.tiempo_maximo_segundos
            or NEWS_SYNC_DEFAULT_LOCK_SECONDS
        )

        lock_acquired = (
            await self._operation_repository
            .acquire_process_lock(
                process_type="CARGA_MERCADO",
                lock_key=lock_key,
                owner=NEWS_SYNC_LOCK_OWNER,
                process_id=process_id,
                duration_seconds=(
                    lock_seconds
                ),
                entity_type="ACTIVO",
                entity_id=str(asset.id),
                metadata={
                    "asset_id": str(asset.id),
                    "symbol": asset.simbolo,
                    "source": source.nombre,
                    "job": NEWS_SYNC_JOB_CODE,
                    "requested_by": (
                        str(requested_by)
                        if requested_by
                        is not None
                        else None
                    ),
                },
            )
        )

        if not lock_acquired:
            await (
                self._operation_repository
                .rollback()
            )

            raise ProcessLockUnavailableError(
                "Las noticias del activo "
                "ya están siendo sincronizadas "
                "por otro proceso"
            )

        try:
            execution = (
                await self._operation_repository
                .create_execution(
                    job_id=job.id,
                    requested_by=requested_by,
                    process_id=process_id,
                    trigger=trigger,
                )
            )

            await (
                self._operation_repository
                .commit()
            )

        except Exception:
            await (
                self._operation_repository
                .rollback()
            )

            raise

        try:
            documents = (
                await self._provider.fetch_news(
                    symbol=asset.simbolo,
                    start_at=start_at,
                    end_at=end_at,
                    limit=limit,
                )
            )

            created = 0
            reused = 0
            failed = 0

            for document in documents:
                try:
                    result = (
                        await self._storage
                        .store_for_asset(
                            asset_id=asset.id,
                            document=document,
                            provider_name=(
                                self._provider
                                .source_name
                            ),
                            language=None,
                        )
                    )

                    if result.mongo_created:
                        created += 1
                    else:
                        reused += 1

                except NewsPersistenceError:
                    failed += 1

            synchronized_at = (
                datetime.now(UTC)
            )

            result_data = {
                "asset_id": str(
                    asset.id
                ),
                "symbol": asset.simbolo,
                "source_id": str(
                    source.id
                ),
                "source_name": (
                    source.nombre
                ),
                "received": len(
                    documents
                ),
                "created": created,
                "reused": reused,
                "failed": failed,
            }

            await (
                self._operation_repository
                .mark_completed(
                    execution,
                    processed=len(
                        documents
                    ),
                    successful=(
                        created + reused
                    ),
                    failed=failed,
                    result=result_data,
                )
            )

            await (
                self._operation_repository
                .update_job_last_execution(
                    job
                )
            )

            await (
                self._operation_repository
                .release_process_lock(
                    lock_key=lock_key,
                    process_id=process_id,
                )
            )

            await (
                self._operation_repository
                .commit()
            )

        except Exception as error:
            await (
                self._operation_repository
                .rollback()
            )

            current_execution = (
                await self._operation_repository
                .get_execution(
                    execution.id
                )
            )

            if current_execution is not None:
                await (
                    self._operation_repository
                    .mark_failed(
                        current_execution,
                        message=str(
                            error
                        )[:2000],
                    )
                )

            await (
                self._operation_repository
                .release_process_lock(
                    lock_key=lock_key,
                    process_id=process_id,
                )
            )

            await (
                self._operation_repository
                .commit()
            )

            from alphainvest.modules.news.domain.exceptions import (
                NewsProviderError,
            )

            if isinstance(
                error,
                NewsProviderError,
            ):
                raise

            raise NewsSynchronizationError(
                "No fue posible completar "
                "la sincronización de noticias"
            ) from error

        return NewsSynchronizationResponse(
            execution_id=execution.id,
            asset_id=asset.id,
            symbol=asset.simbolo,
            source_id=source.id,
            source_name=source.nombre,
            received=len(documents),
            created=created,
            reused=reused,
            failed=failed,
            synchronized_at=(
                synchronized_at
            ),
        )