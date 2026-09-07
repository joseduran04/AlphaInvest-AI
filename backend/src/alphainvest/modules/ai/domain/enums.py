from enum import StrEnum


class AIModelStatus(StrEnum):
    DEVELOPMENT = "DESARROLLO"
    VALIDATION = "VALIDACION"
    ACTIVE = "ACTIVO"
    INACTIVE = "INACTIVO"
    RETIRED = "RETIRADO"