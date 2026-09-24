import asyncio
import logging
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd
import yfinance as yf

from alphainvest.modules.market.domain.exceptions import (
    ProviderRequestError,
    ProviderResponseError,
)
from alphainvest.modules.market.domain.provider_symbols import (
    yahoo_symbol,
)
from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)

logger = logging.getLogger(__name__)


class YahooFinanceProvider:
    """Provider histórico de precios diarios mediante yfinance."""

    source_name = "Yahoo Finance"

    async def fetch_daily_prices(
        self,
        *,
        symbol: str,
        currency: str,
        asset_type: str,
        market_code: str | None = None,
        start_date: date | None = None,
    ) -> list[DailyPricePoint]:
        normalized_symbol = yahoo_symbol(
            symbol=symbol,
            asset_type=asset_type,
            market_code=market_code,
        )

        if not normalized_symbol:
            raise ProviderRequestError(
                "El símbolo financiero no puede estar vacío"
            )

        try:
            history = await asyncio.to_thread(
                self._download_history,
                normalized_symbol,
                start_date,
            )
        except Exception as error:
            raise ProviderRequestError(
                "No fue posible obtener el histórico "
                "desde Yahoo Finance"
            ) from error

        if history.empty:
            raise ProviderResponseError(
                "Yahoo Finance no devolvió precios históricos "
                f"para {normalized_symbol}"
            )

        prices: list[DailyPricePoint] = []

        skipped = 0

        for index, row in history.iterrows():
            try:
                price = self._parse_row(
                    raw_date=index,
                    row=row,
                    currency=currency,
                )
            except (ProviderResponseError, ValueError, InvalidOperation):
                skipped += 1
                continue

            prices.append(price)

        if not prices:
            raise ProviderResponseError(
                "Yahoo Finance no devolvió filas válidas "
                f"para {normalized_symbol}"
            )

        if skipped:
            logger.warning(
                "Yahoo Finance: %s filas inválidas omitidas para %s",
                skipped,
                normalized_symbol,
            )

        return sorted(
            prices,
            key=lambda item: item.date,
        )

    @staticmethod
    def _download_history(
        symbol: str,
        start_date: date | None = None,
    ) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)

        period_arguments: dict[str, Any] = (
            {"start": start_date.isoformat()}
            if start_date is not None
            else {"period": "max"}
        )

        history = ticker.history(
            **period_arguments,
            interval="1d",
            actions=False,
            auto_adjust=False,
            repair=True,
            keepna=False,
            raise_errors=True,
        )

        if not isinstance(history, pd.DataFrame):
            raise ProviderResponseError(
                "Yahoo Finance devolvió una estructura inválida"
            )

        return history

    @staticmethod
    def _parse_row(
        *,
        raw_date: Any,
        row: Any,
        currency: str,
    ) -> DailyPricePoint:
        try:
            timestamp = pd.Timestamp(raw_date)

            open_price = Decimal(str(row["Open"]))
            high_price = Decimal(str(row["High"]))
            low_price = Decimal(str(row["Low"]))
            close_price = Decimal(str(row["Close"]))

            adjusted_value = row.get(
                "Adj Close",
                None,
            )

            adjusted_close = (
                Decimal(str(adjusted_value))
                if adjusted_value is not None
                and not pd.isna(adjusted_value)
                else None
            )

            volume_value = row.get(
                "Volume",
                None,
            )

            # Divisas e índices pueden no traer volumen.
            volume = (
                None
                if volume_value is None
                or pd.isna(volume_value)
                else Decimal(str(volume_value))
            )

        except (
            KeyError,
            InvalidOperation,
            TypeError,
            ValueError,
        ) as error:
            raise ProviderResponseError(
                "Yahoo Finance devolvió una fila OHLCV inválida"
            ) from error

        # Yahoo (con repair=True) a veces entrega máximos/mínimos que no
        # contienen a la apertura o al cierre por redondeos o ajustes. Se
        # amplía el rango en vez de descartar la sesión completa.
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)

        return DailyPricePoint(
            date=timestamp.date(),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            adjusted_close=adjusted_close,
            volume=volume,
            currency=currency.strip().upper(),
        )