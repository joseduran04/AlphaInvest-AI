"""Traducción del símbolo interno de AlphaInvest al símbolo de cada proveedor.

El catálogo usa símbolos "de negocio" (AMXL, USD/MXN, BTC-USD). Cada
proveedor espera su propia convención:

- Yahoo Finance: sufijo ".MX" para la Bolsa Mexicana, "EURUSD=X" para
  divisas y "BTC-USD" para criptoactivos.
- Alpha Vantage NEWS_SENTIMENT: tickers de EE. UU., "FOREX:EUR" y
  "CRYPTO:BTC". Las emisoras mexicanas se buscan por su ADR cuando existe.
"""

MEXICAN_MARKETS = frozenset({"BMV", "BIVA"})

# Excepciones explícitas para Yahoo Finance.
# AMXL: América Móvil unificó sus series; hoy cotiza como serie B (AMXB).
YAHOO_SYMBOL_OVERRIDES: dict[str, str] = {
    "AMXL": "AMXB.MX",
}

# Tickers de noticias para emisoras mexicanas con ADR en EE. UU.
NEWS_TICKER_OVERRIDES: dict[str, str] = {
    "AMXL": "AMX",
    "FEMSAUBD": "FMX",
}


def _normalize(value: str | None) -> str:
    return (value or "").strip().upper()


def yahoo_symbol(
    *,
    symbol: str,
    asset_type: str | None = None,
    market_code: str | None = None,
) -> str:
    """Símbolo que Yahoo Finance reconoce para el activo."""

    normalized = _normalize(symbol)

    if normalized in YAHOO_SYMBOL_OVERRIDES:
        return YAHOO_SYMBOL_OVERRIDES[normalized]

    if _normalize(asset_type) == "DIVISA" and "/" in normalized:
        base, quote = normalized.split("/", 1)
        return f"{base}{quote}=X"

    if (
        _normalize(market_code) in MEXICAN_MARKETS
        and not normalized.endswith(".MX")
    ):
        return f"{normalized}.MX"

    return normalized


def news_ticker(
    *,
    symbol: str,
    asset_type: str | None = None,
    market_code: str | None = None,
) -> str:
    """Ticker que Alpha Vantage NEWS_SENTIMENT reconoce para el activo."""

    normalized = _normalize(symbol)
    normalized_type = _normalize(asset_type)

    if normalized in NEWS_TICKER_OVERRIDES:
        return NEWS_TICKER_OVERRIDES[normalized]

    if normalized_type == "CRIPTO":
        return f"CRYPTO:{normalized.split('-', 1)[0]}"

    if normalized_type == "DIVISA" and "/" in normalized:
        base, quote = normalized.split("/", 1)
        # Se consulta la divisa distinta del dólar (USD/MXN -> MXN).
        return f"FOREX:{quote if base == 'USD' else base}"

    _ = market_code

    return normalized
