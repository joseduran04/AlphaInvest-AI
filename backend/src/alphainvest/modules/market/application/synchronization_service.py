from uuid import UUID, uuid4

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    ProcessLockUnavailableError,
    ScheduledJobNotFoundError,
)
from alphainvest.modules.market.domain.provider import (
    MarketDataProvider,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.market.presentation.schemas import (
    PriceSynchronizationResponse,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)

PRICE_SYNC_JOB_CODE = "ACTUALIZAR_PRECIOS_DIARIOS"
PRICE_SYNC_LOCK_PREFIX = "MARKET_PRICE_SYNC"
PRICE_SYNC_LOCK_OWNER = "alphainvest-api"
PRICE_SYNC_LOCK_DURATION_SECONDS = 120


class PriceSynchronizationService:
    """Sincroniza precios con registro operativo y bloqueo."""

    def __init__(
        self,
        *,
        market_repository: MarketRepository,
        operation_repository: OperationRepository,
        provider: MarketDataProvider,
    ) -> None:
        self._market_repository = market_repository
        self._operation_repository = operation_repository
        self._provider = provider

    async def synchronize_asset(
        self,
        *,
        asset_id: UUID,
        requested_by: UUID | None,
    ) -> PriceSynchronizationResponse:
        asset = await self._market_repository.get_asset(
            asset_id
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
                "No existe una fuente financiera activa "
                f"llamada {self._provider.source_name}"
            )

        job = await self._operation_repository.get_job_by_code(
            PRICE_SYNC_JOB_CODE
        )

        if job is None:
            raise ScheduledJobNotFoundError(
                "No existe el trabajo operativo "
                "ACTUALIZAR_PRECIOS_DIARIOS"
            )

        process_id = (
            f"PRICE_SYNC_{asset.id}_{uuid4().hex}"
        )
        lock_key = (
            f"{PRICE_SYNC_LOCK_PREFIX}:{asset.id}"
        )

        lock_acquired = (
            await self._operation_repository
            .acquire_process_lock(
                process_type="CARGA_MERCADO",
                lock_key=lock_key,
                owner=PRICE_SYNC_LOCK_OWNER,
                process_id=process_id,
                duration_seconds=(
                    PRICE_SYNC_LOCK_DURATION_SECONDS
                ),
                entity_type="ACTIVO",
                entity_id=str(asset.id),
                metadata={
                    "asset_id": str(asset.id),
                    "symbol": asset.simbolo,
                    "source": source.nombre,
                    "requested_by": (
                        str(requested_by)
                        if requested_by is not None
                        else None
                    ),
                },
            )
        )

        if not lock_acquired:
            await self._operation_repository.rollback()

            raise ProcessLockUnavailableError(
                "El activo ya está siendo sincronizado "
                "por otro proceso"
            )

        try:
            execution = (
                await self._operation_repository.create_execution(
                    job_id=job.id,
                    requested_by=requested_by,
                    process_id=process_id,
                )
            )

            # Persiste conjuntamente el bloqueo y la ejecución
            # en estado EJECUTANDO.
            await self._operation_repository.commit()

        except Exception:
            await self._operation_repository.rollback()
            raise

        try:
            prices = await self._provider.fetch_daily_prices(
                symbol=asset.simbolo,
                currency=asset.moneda,
            )

            price_dates = [
                price.date
                for price in prices
            ]

            existing_dates = (
                await self._market_repository
                .get_existing_price_dates(
                    asset_id=asset.id,
                    source_id=source.id,
                    dates=price_dates,
                )
            )

            created = sum(
                1
                for price_date in price_dates
                if price_date not in existing_dates
            )
            updated = len(price_dates) - created

            await self._market_repository.upsert_daily_prices(
                asset_id=asset.id,
                source_id=source.id,
                prices=prices,
            )

            synchronized_at = (
                await self._market_repository
                .mark_source_requested(source)
            )

            result_data = {
                "asset_id": str(asset.id),
                "symbol": asset.simbolo,
                "source_id": str(source.id),
                "source_name": source.nombre,
                "received": len(prices),
                "created": created,
                "updated": updated,
                "first_date": (
                    prices[0].date.isoformat()
                    if prices
                    else None
                ),
                "last_date": (
                    prices[-1].date.isoformat()
                    if prices
                    else None
                ),
            }

            await self._operation_repository.mark_completed(
                execution,
                processed=len(prices),
                successful=len(prices),
                failed=0,
                result=result_data,
            )

            await self._operation_repository.update_job_last_execution(
                job
            )

            await self._operation_repository.release_process_lock(
                lock_key=lock_key,
                process_id=process_id,
            )

            await self._operation_repository.commit()

        except Exception as error:
            await self._operation_repository.rollback()

            current_execution = (
                await self._operation_repository.get_execution(
                    execution.id
                )
            )

            if current_execution is not None:
                await self._operation_repository.mark_failed(
                    current_execution,
                    message=str(error)[:2000],
                )

            await self._operation_repository.release_process_lock(
                lock_key=lock_key,
                process_id=process_id,
            )

            await self._operation_repository.commit()

            raise

        return PriceSynchronizationResponse(
            execution_id=execution.id,
            asset_id=asset.id,
            symbol=asset.simbolo,
            source_id=source.id,
            source_name=source.nombre,
            received=len(prices),
            created=created,
            updated=updated,
            synchronized_at=synchronized_at,
            first_date=prices[0].date if prices else None,
            last_date=prices[-1].date if prices else None,
        )