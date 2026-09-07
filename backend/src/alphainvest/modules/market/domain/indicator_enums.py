from enum import StrEnum


class FinancialIndicatorType(StrEnum):
    SMA = "SMA"
    EMA = "EMA"
    RSI = "RSI"
    VOLATILITY = "VOLATILIDAD"
    MACD = "MACD"
    MACD_SIGNAL = "MACD_SIGNAL"
    MACD_HISTOGRAM = "MACD_HISTOGRAMA"