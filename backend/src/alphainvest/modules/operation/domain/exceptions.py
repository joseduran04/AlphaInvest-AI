class NotificationError(Exception):
    """Excepción base del dominio de notificaciones."""


class NotificationNotFoundError(
    NotificationError
):
    """La notificación solicitada no existe para el usuario."""


class NotificationNotSentError(
    NotificationError
):
    """La notificación todavía no ha sido entregada."""


class InvalidNotificationContentError(
    NotificationError
):
    """El contenido de la notificación no es válido."""


class InvalidNotificationReferenceError(
    NotificationError
):
    """La referencia relacionada con la notificación es inválida."""


class InvalidNotificationStateTransitionError(
    NotificationError
):
    """La transición solicitada no es válida para la notificación."""