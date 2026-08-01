from enum import StrEnum


class JobExecutionStatus(StrEnum):
    PENDING = "PENDIENTE"
    RUNNING = "EJECUTANDO"
    COMPLETED = "COMPLETADA"
    FAILED = "FALLIDA"
    CANCELLED = "CANCELADA"
    SKIPPED = "OMITIDA"


class JobTrigger(StrEnum):
    SCHEDULED = "PROGRAMADO"
    MANUAL = "MANUAL"
    RETRY = "REINTENTO"
    SYSTEM = "SISTEMA"