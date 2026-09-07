from enum import StrEnum


class SimulationType(StrEnum):
    HISTORICAL = "HISTORICA"
    MONTE_CARLO = "MONTE_CARLO"
    PROJECTION = "PROYECCION"
    SCENARIO = "ESCENARIO"


class SimulationConfigurationStatus(StrEnum):
    DRAFT = "BORRADOR"
    READY = "LISTA"
    ARCHIVED = "ARCHIVADA"


class ContributionFrequency(StrEnum):
    WEEKLY = "SEMANAL"
    BIWEEKLY = "QUINCENAL"
    MONTHLY = "MENSUAL"
    QUARTERLY = "TRIMESTRAL"
    SEMIANNUAL = "SEMESTRAL"
    ANNUAL = "ANUAL"


class SimulationExecutionStatus(StrEnum):
    PENDING = "PENDIENTE"
    RUNNING = "EJECUTANDO"
    COMPLETED = "COMPLETADA"
    FAILED = "FALLIDA"
    CANCELLED = "CANCELADA"