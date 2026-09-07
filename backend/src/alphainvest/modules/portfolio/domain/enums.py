from enum import StrEnum


class PortfolioType(StrEnum):
    VIRTUAL = "VIRTUAL"
    SIMULATED = "SIMULADO"


class PortfolioStatus(StrEnum):
    ACTIVE = "ACTIVO"
    CLOSED = "CERRADO"
    ARCHIVED = "ARCHIVADO"


class PositionStatus(StrEnum):
    OPEN = "ABIERTA"
    CLOSED = "CERRADA"