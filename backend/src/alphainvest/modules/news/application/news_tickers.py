from alphainvest.modules.market.domain.provider_symbols import (
    news_ticker,
)


def asset_news_ticker(asset: object) -> str:
    """Ticker de noticias del activo según su tipo y mercado."""

    symbol = getattr(asset, "simbolo", "")
    asset_type = getattr(
        getattr(asset, "tipo_activo", None),
        "codigo",
        None,
    )
    market_code = getattr(
        getattr(asset, "mercado", None),
        "codigo",
        None,
    )

    return news_ticker(
        symbol=symbol if isinstance(symbol, str) else "",
        asset_type=(
            asset_type if isinstance(asset_type, str) else None
        ),
        market_code=(
            market_code if isinstance(market_code, str) else None
        ),
    )
