from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from alphainvest.modules.operation.domain.enums import (
    JobExecutionStatus,
    JobTrigger,
)


class JobSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str = Field(validation_alias="codigo")
    name: str = Field(validation_alias="nombre")
    type: str = Field(validation_alias="tipo")


class JobExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: JobExecutionStatus = Field(
        validation_alias="estado"
    )
    attempt: int = Field(
        validation_alias="numero_intento"
    )
    trigger: JobTrigger = Field(
        validation_alias="disparador"
    )
    requested_by: UUID | None = Field(
        validation_alias="solicitado_por"
    )
    process_id: str | None = Field(
        validation_alias="identificador_proceso"
    )
    requested_at: datetime = Field(
        validation_alias="fecha_solicitud"
    )
    started_at: datetime | None = Field(
        validation_alias="fecha_inicio"
    )
    finished_at: datetime | None = Field(
        validation_alias="fecha_fin"
    )
    progress: Decimal = Field(
        validation_alias="progreso"
    )
    processed_records: int = Field(
        validation_alias="registros_procesados"
    )
    successful_records: int = Field(
        validation_alias="registros_exitosos"
    )
    failed_records: int = Field(
        validation_alias="registros_fallidos"
    )
    result: dict[str, Any] | None = Field(
        validation_alias="resultado"
    )
    error_message: str | None = Field(
        validation_alias="mensaje_error"
    )
    job: JobSummaryResponse = Field(
        validation_alias="trabajo"
    )


class JobExecutionListResponse(BaseModel):
    items: list[JobExecutionResponse]
    total: int
    limit: int
    offset: int