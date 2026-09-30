from enum import StrEnum


class AssetStatus(StrEnum):
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"
    SUSPENDED = "SUSPENDIDO"


class MoversPeriod(StrEnum):
    """Periodo contra el que se comparan las alzas y bajas."""

    DAY = "DIA"
    WEEK = "SEMANA"
    MONTH = "MES"
    YEAR_TO_DATE = "ANIO"
