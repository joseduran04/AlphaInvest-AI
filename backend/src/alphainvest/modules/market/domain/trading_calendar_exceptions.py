class TradingCalendarError(Exception):
    """Error base del calendario bursátil."""


class UnsupportedMarketCalendarError(
    TradingCalendarError
):
    """El mercado no tiene calendario configurado."""


class InvalidTradingSessionError(
    TradingCalendarError
):
    """La fecha base no representa una sesión válida."""


class TradingCalendarRangeError(
    TradingCalendarError
):
    """El calendario no cubre el horizonte requerido."""