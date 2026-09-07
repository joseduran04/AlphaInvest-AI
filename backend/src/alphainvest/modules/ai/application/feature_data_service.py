from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.domain.exceptions import (
    AIFeatureDataUnavailableError,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
    AIFeatureRow,
)
from alphainvest.modules.market.domain.indicator_calculator import (
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
    calculate_volatility,
)
from alphainvest.modules.market.domain.indicator_values import (
    CalculatedIndicatorPoint,
    ClosingPricePoint,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)


class AIFeatureDataService:
    """Construye datasets técnicos desde una fuente de precios concreta."""

    MINIMUM_ROWS = 35

    REQUIRED_INDICATORS = {
        ("SMA", "20D"): "sma_20",
        ("EMA", "20D"): "ema_20",
        ("RSI", "14D"): "rsi_14",
        ("VOLATILIDAD", "30D"): "volatility_30",
        ("MACD", "12-26-9"): "macd",
        ("MACD_SIGNAL", "12-26-9"): "macd_signal",
        (
            "MACD_HISTOGRAMA",
            "12-26-9",
        ): "macd_histogram",
    }

    def __init__(
        self,
        *,
        market_repository: MarketRepository,
        source_name: str,
    ) -> None:
        normalized_source = source_name.strip()

        if not normalized_source:
            raise ValueError(
                "El nombre de la fuente financiera "
                "no puede estar vacío"
            )

        self._market_repository = market_repository
        self._source_name = normalized_source

    async def build_dataset(
        self,
        *,
        asset_id: UUID,
        start_date: date,
        end_date: date,
    ) -> AIFeatureDataset:
        if start_date > end_date:
            raise ValueError(
                "La fecha inicial no puede ser posterior "
                "a la fecha final"
            )

        source = (
            await self._market_repository
            .get_financial_source_by_name(
                name=self._source_name,
                active_only=True,
            )
        )

        if source is None:
            raise AIFeatureDataUnavailableError(
                "La fuente financiera requerida "
                "para IA no está disponible"
            )

        prices = (
            await self._market_repository
            .list_asset_prices_for_simulation(
                asset_id=asset_id,
                source_id=source.id,
                start_date=start_date,
                end_date=end_date,
            )
        )

        if not prices:
            raise AIFeatureDataUnavailableError(
                "No existen precios históricos "
                "para construir el dataset"
            )

        closing_prices = [
            ClosingPricePoint(
                date=price.fecha,
                close=(
                    price.cierre_ajustado
                    if price.cierre_ajustado is not None
                    else price.cierre
                ),
            )
            for price in prices
        ]

        try:
            indicators = self._calculate_indicators(
                closing_prices
            )
        except ValueError as error:
            raise AIFeatureDataUnavailableError(
                "No existen precios suficientes "
                "para calcular las features requeridas"
            ) from error

        indicator_by_date: dict[
            date,
            dict[str, Decimal],
        ] = {}

        for indicator in indicators:
            key = (
                indicator.indicator_type,
                indicator.period,
            )

            feature_name = (
                self.REQUIRED_INDICATORS.get(key)
            )

            if feature_name is None:
                continue

            values = indicator_by_date.setdefault(
                indicator.date,
                {},
            )

            values[feature_name] = indicator.value

        required_features = set(
            self.REQUIRED_INDICATORS.values()
        )

        rows: list[AIFeatureRow] = []

        for price in prices:
            indicator_values = indicator_by_date.get(
                price.fecha
            )

            if indicator_values is None:
                continue

            if not required_features.issubset(
                indicator_values
            ):
                continue

            close = (
                price.cierre_ajustado
                if price.cierre_ajustado is not None
                else price.cierre
            )

            rows.append(
                AIFeatureRow(
                    asset_id=asset_id,
                    date=price.fecha,
                    close=close,
                    volume=price.volumen,
                    sma_20=indicator_values[
                        "sma_20"
                    ],
                    ema_20=indicator_values[
                        "ema_20"
                    ],
                    rsi_14=indicator_values[
                        "rsi_14"
                    ],
                    volatility_30=indicator_values[
                        "volatility_30"
                    ],
                    macd=indicator_values[
                        "macd"
                    ],
                    macd_signal=indicator_values[
                        "macd_signal"
                    ],
                    macd_histogram=indicator_values[
                        "macd_histogram"
                    ],
                )
            )

        if len(rows) < self.MINIMUM_ROWS:
            raise AIFeatureDataUnavailableError(
                "No existen suficientes fechas con "
                "todas las features requeridas. "
                f"Disponibles: {len(rows)}; "
                f"mínimo: {self.MINIMUM_ROWS}"
            )

        return AIFeatureDataset(
            asset_id=asset_id,
            source_id=source.id,
            start_date=rows[0].date,
            end_date=rows[-1].date,
            rows=tuple(rows),
        )

    @staticmethod
    def _calculate_indicators(
        prices: list[ClosingPricePoint],
    ) -> list[CalculatedIndicatorPoint]:
        indicators: list[
            CalculatedIndicatorPoint
        ] = []

        indicators.extend(
            calculate_sma(
                prices,
                period=20,
            )
        )

        indicators.extend(
            calculate_ema(
                prices,
                period=20,
            )
        )

        indicators.extend(
            calculate_rsi(
                prices,
                period=14,
            )
        )

        indicators.extend(
            calculate_volatility(
                prices,
                period=30,
            )
        )

        indicators.extend(
            calculate_macd(
                prices,
                fast_period=12,
                slow_period=26,
                signal_period=9,
            )
        )

        return indicators