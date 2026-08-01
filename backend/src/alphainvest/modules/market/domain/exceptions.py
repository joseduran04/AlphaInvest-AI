class MarketError(Exception):
    """Excepción base del módulo Market."""


class AssetNotFoundError(MarketError):
    """El activo solicitado no existe."""


class FinancialSourceNotFoundError(MarketError):
    """La fuente financiera solicitada no existe."""


class HistoricalPriceNotFoundError(MarketError):
    """No existen precios históricos para el activo."""


class InvalidPriceDateRangeError(MarketError):
    """El rango de fechas solicitado no es válido."""


class MarketProviderError(MarketError):
    """Error base al consumir un proveedor financiero."""


class ProviderConfigurationError(MarketProviderError):
    """La configuración del proveedor está incompleta."""


class ProviderRequestError(MarketProviderError):
    """No fue posible completar la solicitud HTTP."""


class ProviderResponseError(MarketProviderError):
    """El proveedor devolvió una respuesta inválida."""


class ProviderRateLimitError(MarketProviderError):
    """El proveedor rechazó la solicitud por límites de uso."""


class PriceSynchronizationError(MarketError):
    """No fue posible guardar la sincronización de precios."""