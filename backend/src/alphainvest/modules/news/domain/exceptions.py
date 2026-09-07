class NewsError(Exception):
    """Excepción base del módulo News."""


class NewsProviderError(NewsError):
    """Error base al consumir un proveedor de noticias."""


class NewsProviderConfigurationError(
    NewsProviderError
):
    """La configuración del proveedor está incompleta."""


class NewsProviderRequestError(
    NewsProviderError
):
    """No fue posible completar la solicitud externa."""


class NewsProviderResponseError(
    NewsProviderError
):
    """El proveedor devolvió una respuesta inválida."""


class NewsProviderRateLimitError(
    NewsProviderError
):
    """El proveedor rechazó la solicitud por límites de uso."""


class NewsPersistenceError(NewsError):
    """No fue posible conservar consistentemente una noticia."""


class NewsDocumentNotFoundError(
    NewsError
):
    """La referencia existe pero el documento MongoDB no."""


class InvalidNewsDateRangeError(
    NewsError
):
    """El rango temporal solicitado para noticias no es válido."""


class NewsSynchronizationError(
    NewsError
):
    """Falló la sincronización operativa de noticias."""