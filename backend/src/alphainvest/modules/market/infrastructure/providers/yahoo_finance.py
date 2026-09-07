import asyncio
from decimal import Decimal, InvalidOperation
from typing import Any

import pandas as pd
import yfinance as yf

from alphainvest.modules.market.domain.exceptions import (
    ProviderRequestError,
    ProviderResponseError,
)
from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)


class YahooFinanceProvider:
    """Provider histórico de precios diarios mediante yfinance."""

    source_name = "Yahoo Finance"

    async def fetch_daily_prices(
        self,
        *,
        symbol: str,
        currency: str,
    ) -> list[DailyPricePoint]:
        normalized_symbol = symbol.strip().upper()

        if not normalized_symbol:
            raise ProviderRequestError(
                "El símbolo financiero no puede estar vacío"
            )

        try:
            history = await asyncio.to_thread(
                self._download_history,
                normalized_symbol,
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

        for index, row in history.iterrows():
            price = self._parse_row(
                raw_date=index,
                row=row,
                currency=currency,
            )

            prices.append(price)

        return sorted(
            prices,
            key=lambda item: item.date,
        )

    @staticmethod
    def _download_history(
        symbol: str,
    ) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)

        history = ticker.history(
            period="max",
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

            if (
                volume_value is None
                or pd.isna(volume_value)
            ):
                raise ProviderResponseError(
                    "Yahoo Finance devolvió volumen inválido"
                )

            volume = Decimal(
                str(volume_value)
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