from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from alphainvest.modules.market.domain.exceptions import (
    ProviderConfigurationError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderResponseError,
)
from alphainvest.modules.market.domain.value_objects import (
    DailyPricePoint,
)


class AlphaVantageProvider:
    """Adaptador para precios diarios de Alpha Vantage."""

    source_name = "Alpha Vantage"

    def __init__(
        self,
        *,
        api_key: str | None,
        base_url: str,
        timeout_seconds: float,
        output_size: str = "compact",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_key = (
            api_key.strip()
            if api_key is not None
            else None
        )
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._output_size = output_size
        self._client = client

    async def fetch_daily_prices(
        self,
        *,
        symbol: str,
        currency: str,
        asset_type: str,
        market_code: str | None = None,
    ) -> list[DailyPricePoint]:
        _ = market_code
        if not self._api_key:
            raise ProviderConfigurationError(
                "No se configuró la API key de Alpha Vantage"
            )

        normalized_symbol = symbol.strip().upper()
        normalized_currency = currency.strip().upper()
        normalized_asset_type = asset_type.strip().upper()

        if not normalized_symbol:
            raise ProviderConfigurationError(
                "El símbolo financiero no puede estar vacío"
            )

        if len(normalized_currency) != 3:
            raise ProviderConfigurationError(
                "La moneda del activo debe contener tres caracteres"
            )

        if normalized_asset_type == "DIVISA":
            return await self._fetch_forex_daily_prices(
                symbol=normalized_symbol,
                currency=normalized_currency,
            )

        if normalized_asset_type == "CRIPTO":
            return await self._fetch_crypto_daily_prices(
                symbol=normalized_symbol,
                currency=normalized_currency,
            )

        return await self._fetch_standard_daily_prices(
            symbol=normalized_symbol,
            currency=normalized_currency,
        )

    async def _fetch_standard_daily_prices(
        self,
        *,
        symbol: str,
        currency: str,
    ) -> list[DailyPricePoint]:
        payload = await self._request(
            params={
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "outputsize": self._output_size,
                "datatype": "json",
                "apikey": self._api_key or "",
            }
        )

        self._validate_provider_response(payload)

        raw_series = payload.get("Time Series (Daily)")

        if not isinstance(raw_series, dict):
            raise ProviderResponseError(
                "Alpha Vantage no devolvió una serie diaria"
            )

        prices = [
            self._parse_standard_price(
                raw_date=raw_date,
                raw_values=raw_values,
                currency=currency,
            )
            for raw_date, raw_values in raw_series.items()
        ]

        return sorted(
            prices,
            key=lambda item: item.date,
        )

    async def _fetch_forex_daily_prices(
        self,
        *,
        symbol: str,
        currency: str,
    ) -> list[DailyPricePoint]:
        base_symbol, quote_symbol = self._split_pair_symbol(
            symbol,
            asset_type="DIVISA",
        )

        if quote_symbol != currency:
            raise ProviderConfigurationError(
                "La moneda de la divisa no coincide con "
                "la moneda cotizada del símbolo"
            )

        payload = await self._request(
            params={
                "function": "FX_DAILY",
                "from_symbol": base_symbol,
                "to_symbol": quote_symbol,
                "outputsize": self._output_size,
                "datatype": "json",
                "apikey": self._api_key or "",
            }
        )

        self._validate_provider_response(payload)

        raw_series = payload.get("Time Series FX (Daily)")

        if not isinstance(raw_series, dict):
            raise ProviderResponseError(
                "Alpha Vantage no devolvió una serie diaria de divisas"
            )

        prices = [
            self._parse_forex_price(
                raw_date=raw_date,
                raw_values=raw_values,
                currency=currency,
            )
            for raw_date, raw_values in raw_series.items()
        ]

        return sorted(
            prices,
            key=lambda item: item.date,
        )

    async def _fetch_crypto_daily_prices(
        self,
        *,
        symbol: str,
        currency: str,
    ) -> list[DailyPricePoint]:
        crypto_symbol, market_currency = self._split_pair_symbol(
            symbol,
            asset_type="CRIPTO",
        )

        if market_currency != currency:
            raise ProviderConfigurationError(
                "La moneda del criptoactivo no coincide con "
                "la moneda cotizada del símbolo"
            )

        payload = await self._request(
            params={
                "function": "DIGITAL_CURRENCY_DAILY",
                "symbol": crypto_symbol,
                "market": market_currency,
                "datatype": "json",
                "apikey": self._api_key or "",
            }
        )

        self._validate_provider_response(payload)

        raw_series = payload.get(
            "Time Series (Digital Currency Daily)"
        )

        if not isinstance(raw_series, dict):
            raise ProviderResponseError(
                "Alpha Vantage no devolvió una serie diaria "
                "de criptoactivos"
            )

        prices = [
            self._parse_crypto_price(
                raw_date=raw_date,
                raw_values=raw_values,
                currency=currency,
            )
            for raw_date, raw_values in raw_series.items()
        ]

        return sorted(
            prices,
            key=lambda item: item.date,
        )

    async def _request(
        self,
        *,
        params: dict[str, str],
    ) -> dict[str, Any]:
        try:
            if self._client is not None:
                response = await self._client.get(
                    f"{self._base_url}/query",
                    params=params,
                    timeout=self._timeout_seconds,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self._base_url}/query",
                        params=params,
                        timeout=self._timeout_seconds,
                    )

            response.raise_for_status()

        except httpx.TimeoutException as error:
            raise ProviderRequestError(
                "Alpha Vantage excedió el tiempo de espera"
            ) from error

        except httpx.HTTPStatusError as error:
            raise ProviderRequestError(
                "Alpha Vantage devolvió un estado HTTP "
                f"{error.response.status_code}"
            ) from error

        except httpx.RequestError as error:
            raise ProviderRequestError(
                "No fue posible conectar con Alpha Vantage"
            ) from error

        try:
            payload = response.json()
        except ValueError as error:
            raise ProviderResponseError(
                "Alpha Vantage devolvió JSON inválido"
            ) from error

        if not isinstance(payload, dict):
            raise ProviderResponseError(
                "Alpha Vantage devolvió una estructura inválida"
            )

        return payload

    @staticmethod
    def _validate_provider_response(
        payload: dict[str, Any],
    ) -> None:
        rate_limit_message = payload.get("Note")

        if isinstance(rate_limit_message, str):
            raise ProviderRateLimitError(
                "Alpha Vantage alcanzó su límite de consultas"
            )

        information = payload.get("Information")

        if isinstance(information, str):
            lowered = information.lower()

            if (
                "rate limit" in lowered
                or "frequency" in lowered
            ):
                raise ProviderRateLimitError(
                    "Alpha Vantage alcanzó su límite de consultas"
                )

            raise ProviderResponseError(information)

        error_message = payload.get("Error Message")

        if isinstance(error_message, str):
            raise ProviderResponseError(error_message)

    @staticmethod
    def _split_pair_symbol(
        symbol: str,
        *,
        asset_type: str,
    ) -> tuple[str, str]:
        separator = (
            "/"
            if "/" in symbol
            else "-"
            if "-" in symbol
            else None
        )

        if separator is None:
            raise ProviderConfigurationError(
                f"El símbolo de tipo {asset_type} debe contener "
                "un par separado por '/' o '-'"
            )

        parts = symbol.split(separator)

        if len(parts) != 2:
            raise ProviderConfigurationError(
                f"El símbolo de tipo {asset_type} tiene "
                "un formato inválido"
            )

        base_symbol = parts[0].strip().upper()
        quote_symbol = parts[1].strip().upper()

        if not base_symbol or not quote_symbol:
            raise ProviderConfigurationError(
                f"El símbolo de tipo {asset_type} tiene "
                "un formato inválido"
            )

        if len(quote_symbol) != 3:
            raise ProviderConfigurationError(
                "La moneda cotizada debe contener tres caracteres"
            )

        if asset_type == "DIVISA" and len(base_symbol) != 3:
            raise ProviderConfigurationError(
                "La moneda base de la divisa debe contener "
                "tres caracteres"
            )

        return base_symbol, quote_symbol

    @staticmethod
    def _parse_standard_price(
        *,
        raw_date: object,
        raw_values: object,
        currency: str,
    ) -> DailyPricePoint:
        if not isinstance(raw_date, str):
            raise ProviderResponseError(
                "Alpha Vantage devolvió una fecha inválida"
            )

        if not isinstance(raw_values, dict):
            raise ProviderResponseError(
                "Alpha Vantage devolvió un precio inválido"
            )

        try:
            price_date = date.fromisoformat(raw_date)
            open_price = Decimal(str(raw_values["1. open"]))
            high_price = Decimal(str(raw_values["2. high"]))
            low_price = Decimal(str(raw_values["3. low"]))
            close_price = Decimal(str(raw_values["4. close"]))
            volume = Decimal(str(raw_values["5. volume"]))

        except (
            KeyError,
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:
            raise ProviderResponseError(
                "Alpha Vantage devolvió campos OHLCV inválidos"
            ) from error

        return DailyPricePoint(
            date=price_date,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            adjusted_close=None,
            volume=volume,
            currency=currency,
        )

    @staticmethod
    def _parse_forex_price(
        *,
        raw_date: object,
        raw_values: object,
        currency: str,
    ) -> DailyPricePoint:
        if not isinstance(raw_date, str):
            raise ProviderResponseError(
                "Alpha Vantage devolvió una fecha inválida"
            )

        if not isinstance(raw_values, dict):
            raise ProviderResponseError(
                "Alpha Vantage devolvió un precio de divisa inválido"
            )

        try:
            price_date = date.fromisoformat(raw_date)
            open_price = Decimal(str(raw_values["1. open"]))
            high_price = Decimal(str(raw_values["2. high"]))
            low_price = Decimal(str(raw_values["3. low"]))
            close_price = Decimal(str(raw_values["4. close"]))

        except (
            KeyError,
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:
            raise ProviderResponseError(
                "Alpha Vantage devolvió campos OHLC "
                "de divisa inválidos"
            ) from error

        return DailyPricePoint(
            date=price_date,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            adjusted_close=None,
            volume=None,
            currency=currency,
        )

    @classmethod
    def _parse_crypto_price(
        cls,
        *,
        raw_date: object,
        raw_values: object,
        currency: str,
    ) -> DailyPricePoint:
        if not isinstance(raw_date, str):
            raise ProviderResponseError(
                "Alpha Vantage devolvió una fecha inválida"
            )

        if not isinstance(raw_values, dict):
            raise ProviderResponseError(
                "Alpha Vantage devolvió un precio "
                "de criptoactivo inválido"
            )

        try:
            price_date = date.fromisoformat(raw_date)

            open_price = cls._get_crypto_decimal(
                raw_values,
                prefix="1a. open",
                fallback="1. open",
            )
            high_price = cls._get_crypto_decimal(
                raw_values,
                prefix="2a. high",
                fallback="2. high",
            )
            low_price = cls._get_crypto_decimal(
                raw_values,
                prefix="3a. low",
                fallback="3. low",
            )
            close_price = cls._get_crypto_decimal(
                raw_values,
                prefix="4a. close",
                fallback="4. close",
            )
            volume = Decimal(str(raw_values["5. volume"]))

        except (
            KeyError,
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:
            raise ProviderResponseError(
                "Alpha Vantage devolvió campos OHLCV "
                "de criptoactivo inválidos"
            ) from error

        return DailyPricePoint(
            date=price_date,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            adjusted_close=None,
            volume=volume,
            currency=currency,
        )

    @staticmethod
    def _get_crypto_decimal(
        raw_values: dict[object, object],
        *,
        prefix: str,
        fallback: str,
    ) -> Decimal:
        if fallback in raw_values:
            return Decimal(str(raw_values[fallback]))

        for key, value in raw_values.items():
            if (
                isinstance(key, str)
                and key.startswith(prefix)
            ):
                return Decimal(str(value))

        raise KeyError(prefix)