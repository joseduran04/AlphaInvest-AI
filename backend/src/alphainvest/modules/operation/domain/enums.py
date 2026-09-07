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


class NotificationType(StrEnum):
    SYSTEM = "SISTEMA"
    SECURITY = "SEGURIDAD"
    PRICE_ALERT = "ALERTA_PRECIO"
    SIMULATION = "SIMULACION"
    AI_ANALYSIS = "ANALISIS_IA"
    RECOMMENDATION = "RECOMENDACION"
    PORTFOLIO = "PORTAFOLIO"
    MAINTENANCE = "MANTENIMIENTO"
    OTHER = "OTRA"


class NotificationChannel(StrEnum):
    APPLICATION = "APLICACION"
    EMAIL = "CORREO"
    PUSH = "PUSH"


class NotificationChannelCapability(StrEnum):
    INTERNAL = "INTERNO"
    EXTERNAL = "EXTERNO"


class NotificationPriority(StrEnum):
    LOW = "BAJA"
    NORMAL = "NORMAL"
    HIGH = "ALTA"
    URGENT = "URGENTE"


class NotificationStatus(StrEnum):
    PENDING = "PENDIENTE"
    SCHEDULED = "PROGRAMADA"
    SENDING = "ENVIANDO"
    SENT = "ENVIADA"
    FAILED = "FALLIDA"
    CANCELLED = "CANCELADA"