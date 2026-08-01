from uuid import UUID

from alphainvest.modules.market.domain.exceptions import (
    JobExecutionNotFoundError,
)
from alphainvest.modules.operation.domain.enums import (
    JobExecutionStatus,
)
from alphainvest.modules.operation.infrastructure.repository import (
    OperationRepository,
)
from alphainvest.modules.operation.presentation.schemas import (
    JobExecutionListResponse,
    JobExecutionResponse,
)

PRICE_SYNC_JOB_CODE = "ACTUALIZAR_PRECIOS_DIARIOS"


class MarketExecutionService:
    """Consulta ejecuciones de sincronización de mercado."""

    def __init__(
        self,
        repository: OperationRepository,
    ) -> None:
        self._repository = repository

    async def list_synchronizations(
        self,
        *,
        status: JobExecutionStatus | None,
        limit: int,
        offset: int,
    ) -> JobExecutionListResponse:
        executions, total = (
            await self._repository.list_executions(
                job_code=PRICE_SYNC_JOB_CODE,
                status=(
                    status.value
                    if status is not None
                    else None
                ),
                limit=limit,
                offset=offset,
            )
        )

        return JobExecutionListResponse(
            items=[
                JobExecutionResponse.model_validate(execution)
                for execution in executions
            ],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_synchronization(
        self,
        execution_id: UUID,
    ) -> JobExecutionResponse:
        execution = await self._repository.get_execution(
            execution_id
        )

        if (
            execution is None
            or execution.trabajo.codigo
            != PRICE_SYNC_JOB_CODE
        ):
            raise JobExecutionNotFoundError(
                "La ejecución solicitada no existe"
            )

        return JobExecutionResponse.model_validate(
            execution
        )