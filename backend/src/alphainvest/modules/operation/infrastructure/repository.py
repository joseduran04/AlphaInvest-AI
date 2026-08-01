from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import bindparam, func, select, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.operation.domain.enums import (
    JobExecutionStatus,
    JobTrigger,
)
from alphainvest.modules.operation.infrastructure.models import (
    JobExecutionModel,
    ScheduledJobModel,
)


class OperationRepository:
    """Acceso a trabajos y ejecuciones operativas."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_job_by_code(
        self,
        code: str,
    ) -> ScheduledJobModel | None:
        statement = select(ScheduledJobModel).where(
            ScheduledJobModel.codigo == code,
            ScheduledJobModel.activo.is_(True),
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_active_scheduled_jobs(
        self,
    ) -> list[ScheduledJobModel]:
        statement = (
            select(ScheduledJobModel)
            .where(
                ScheduledJobModel.activo.is_(True),
                ScheduledJobModel.tipo.in_(
                    ["CRON", "INTERVALO"]
                ),
            )
            .order_by(ScheduledJobModel.codigo.asc())
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def update_job_next_execution(
        self,
        job: ScheduledJobModel,
        next_execution: datetime | None,
    ) -> None:
        job.siguiente_ejecucion = next_execution
        await self._session.flush()

    async def create_execution(
        self,
        *,
        job_id: UUID,
        requested_by: UUID | None,
        process_id: str,
    ) -> JobExecutionModel:
        execution = JobExecutionModel(
            trabajo_id=job_id,
            estado=JobExecutionStatus.RUNNING.value,
            numero_intento=1,
            disparador=JobTrigger.MANUAL.value,
            solicitado_por=requested_by,
            identificador_proceso=process_id,
        )

        self._session.add(execution)
        await self._session.flush()
        await self._session.refresh(execution)

        return execution

    async def mark_completed(
        self,
        execution: JobExecutionModel,
        *,
        processed: int,
        successful: int,
        failed: int,
        result: dict[str, Any],
    ) -> None:
        execution.estado = JobExecutionStatus.COMPLETED.value
        execution.progreso = Decimal("100")
        execution.registros_procesados = processed
        execution.registros_exitosos = successful
        execution.registros_fallidos = failed
        execution.resultado = result
        execution.mensaje_error = None

        await self._session.flush()
        await self._session.refresh(execution)

    async def mark_failed(
        self,
        execution: JobExecutionModel,
        *,
        message: str,
    ) -> None:
        execution.estado = JobExecutionStatus.FAILED.value
        execution.mensaje_error = message
        execution.registros_fallidos = (
            execution.registros_procesados
        )

        await self._session.flush()
        await self._session.refresh(execution)

    async def update_job_last_execution(
        self,
        job: ScheduledJobModel,
    ) -> None:
        job.ultima_ejecucion = func.now()
        await self._session.flush()

    async def get_execution(
        self,
        execution_id: UUID,
    ) -> JobExecutionModel | None:
        statement = (
            select(JobExecutionModel)
            .where(JobExecutionModel.id == execution_id)
            .options(
                selectinload(JobExecutionModel.trabajo)
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_executions(
        self,
        *,
        job_code: str,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[JobExecutionModel], int]:
        filters = [
            ScheduledJobModel.codigo == job_code
        ]

        if status is not None:
            filters.append(
                JobExecutionModel.estado == status
            )

        statement = (
            select(JobExecutionModel)
            .join(JobExecutionModel.trabajo)
            .where(*filters)
            .options(
                selectinload(JobExecutionModel.trabajo)
            )
            .order_by(
                JobExecutionModel.fecha_solicitud.desc()
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(func.count(JobExecutionModel.id))
            .join(JobExecutionModel.trabajo)
            .where(*filters)
        )

        result = await self._session.execute(statement)
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def acquire_process_lock(
        self,
        *,
        process_type: str,
        lock_key: str,
        owner: str,
        process_id: str,
        duration_seconds: int,
        entity_type: str | None = None,
        entity_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Adquiere un bloqueo lógico mediante PostgreSQL."""

        statement = text(
            """
            SELECT operation.fn_adquirir_bloqueo(
                :process_type,
                :lock_key,
                :owner,
                :process_id,
                make_interval(secs => :duration_seconds),
                :entity_type,
                :entity_id,
                :metadata
            )
            """
        ).bindparams(
            bindparam(
                "metadata",
                type_=JSONB,
            )
        )

        result = await self._session.execute(
            statement,
            {
                "process_type": process_type,
                "lock_key": lock_key,
                "owner": owner,
                "process_id": process_id,
                "duration_seconds": duration_seconds,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "metadata": metadata,
            },
        )

        return bool(result.scalar_one())

    async def release_process_lock(
        self,
        *,
        lock_key: str,
        process_id: str,
    ) -> bool:
        """Libera el bloqueo propiedad del proceso."""

        statement = text(
            """
            SELECT operation.fn_liberar_bloqueo(
                :lock_key,
                :process_id
            )
            """
        )

        result = await self._session.execute(
            statement,
            {
                "lock_key": lock_key,
                "process_id": process_id,
            },
        )

        return bool(result.scalar_one())

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()