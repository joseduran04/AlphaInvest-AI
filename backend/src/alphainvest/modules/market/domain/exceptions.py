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