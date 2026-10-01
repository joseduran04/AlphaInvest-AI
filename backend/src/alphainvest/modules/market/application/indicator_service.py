from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    InvalidIndicatorParametersError,
    InvalidPriceDateRangeError,
)
from alphainvest.modules.market.domain.indicator_calculator import (
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
    calculate_volatility,
)
from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
)
from alphainvest.modules.market.domain.indicator_values import (
    CalculatedIndicatorPoint,
    ClosingPricePoint,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.market.presentation.schemas import (
    FinancialIndicatorListResponse,
    FinancialIndicatorResponse,
    IndicatorCalculationSpec,
)

# Sin fecha inicial, se muestran los últimos dos años.
DEFAULT_WINDOW_DAYS = 730

# Indicadores que se muestran cuando no se pide uno en particular.
DEFAULT_SPECS: tuple[IndicatorCalculationSpec, ...] = (
    IndicatorCalculationSpec(
        indicator_type=FinancialIndicatorType.SMA,
        period=20,
    ),
    IndicatorCalculationSpec(
        indicator_type=FinancialIndicatorType.EMA,
        period=20,
    ),
    IndicatorCalculationSpec(
        indicator_type=FinancialIndicatorType.RSI,
        period=14,
    ),
    IndicatorCalculationSpec(
        indicator_type=FinancialIndicatorType.VOLATILITY,
        period=30,
    ),
    IndicatorCalculationSpec(
        indicator_type=FinancialIndicatorType.MACD,
        fast_period=12,
        slow_period=26,
        signal_period=9,
    ),
)

MACD_FAMILY = frozenset(
    {
        FinancialIndicatorType.MACD,
        FinancialIndicatorType.MACD_SIGNAL,
        FinancialIndicatorType.MACD_HISTOGRAM,
    }
)


def _warmup_days(spec: IndicatorCalculationSpec) -> int:
    """Días naturales previos que necesita el indicador para estabilizarse.

    Las medias exponenciales y el RSI dependen de los días anteriores;
    con este margen el valor coincide con el calculado sobre todo el
    historial.
    """

    if spec.indicator_type == FinancialIndicatorType.MACD:
        sessions = (spec.slow_period or 0) + (spec.signal_period or 0)
    else:
        sessions = spec.period or 0

    return 2 * sessions + 365


def _resolve_specs(
    indicator_type: FinancialIndicatorType | None,
    period: str | None,
) -> tuple[IndicatorCalculationSpec, ...]:
    """Indicadores a calcular según el filtro de la consulta."""

    if indicator_type is None:
        if period is not None:
            raise InvalidIndicatorParametersError(
                "Indica el tipo de indicador junto con el periodo"
            )

        return DEFAULT_SPECS

    is_macd = indicator_type in MACD_FAMILY

    if period is None:
        return tuple(
            spec
            for spec in DEFAULT_SPECS
            if spec.indicator_type == indicator_type
            or (
                is_macd
                and spec.indicator_type == FinancialIndicatorType.MACD
            )
        )

    normalized = period.strip().upper()

    try:
        if is_macd:
            fast, slow, signal = (
                int(value) for value in normalized.split("-")
            )
            return (
                IndicatorCalculationSpec(
                    indicator_type=FinancialIndicatorType.MACD,
                    fast_period=fast,
                    slow_period=slow,
                    signal_period=signal,
                ),
            )

        return (
            IndicatorCalculationSpec(
                indicator_type=indicator_type,
                period=int(normalized.removesuffix("D")),
            ),
        )
    except ValueError as error:
        raise InvalidIndicatorParametersError(
            "El periodo no corresponde al indicador solicitado"
        ) from error


def _matches_type(
    point: CalculatedIndicatorPoint,
    indicator_type: FinancialIndicatorType | None,
) -> bool:
    if indicator_type is None:
        return True

    if indicator_type == FinancialIndicatorType.MACD:
        return point.indicator_type in MACD_FAMILY

    return point.indicator_type == indicator_type


class FinancialIndicatorService:
    """Calcula indicadores técnicos al momento, sin guardarlos.

    Los indicadores se derivan de los precios ya guardados, así que no
    se persisten: se calculan al consultarlos con un margen previo para
    que coincidan con el cálculo sobre el historial completo.
    """

    def __init__(
        self,
        repository: MarketRepository,
    ) -> None:
        self._repository = repository

    async def list_indicators(
        self,
        *,
        asset_id: UUID,
        indicator_type: FinancialIndicatorType | None,
        period: str | None,
        start_date: date | None,
        end_date: date | None,
        limit: int,
        offset: int,
        preferred_source_name: str,
    ) -> FinancialIndicatorListResponse:
        asset = await self._repository.get_asset(
            asset_id
        )

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        if (
            start_date is not None
            and end_date is not None
            and start_date > end_date
        ):
            raise InvalidPriceDateRangeError(
                "La fecha inicial no puede ser mayor "
                "que la fecha final"
            )

        specs = _resolve_specs(indicator_type, period)

        window_start = start_date or (
            (end_date or datetime.now(UTC).date())
            - timedelta(days=DEFAULT_WINDOW_DAYS)
        )

        points: list[CalculatedIndicatorPoint] = []
        source_name = ""

        source = await self._repository.get_indicator_price_source(
            asset_id=asset.id,
            preferred_source_name=preferred_source_name,
        )

        if source is not None:
            source_id, source_name = source

            prices = await (
                self._repository
                .list_closing_prices_for_indicators(
                    asset_id=asset.id,
                    source_id=source_id,
                    since=window_start
                    - timedelta(
                        days=max(_warmup_days(spec) for spec in specs)
                    ),
                    until=end_date,
                )
            )

            for spec in specs:
                try:
                    calculated = self._calculate(
                        prices=prices,
                        calculation=spec,
                    )
                except ValueError:
                    # Historial insuficiente para este indicador.
                    continue

                points.extend(
                    point
                    for point in calculated
                    if point.date >= window_start
                    and _matches_type(point, indicator_type)
                )

        points.sort(
            key=lambda point: (point.indicator_type, point.period)
        )
        points.sort(key=lambda point: point.date, reverse=True)

        calculated_at = datetime.now(UTC)
        page = points[offset:offset + limit]

        return FinancialIndicatorListResponse(
            asset_id=asset.id,
            items=[
                FinancialIndicatorResponse.model_validate(
                    {
                        "id": offset + index + 1,
                        "activo_id": asset.id,
                        "tipo_indicador": point.indicator_type,
                        "fecha": point.date,
                        "valor": point.value,
                        "periodo": point.period,
                        "parametros": {
                            **point.parameters,
                            "price_source_name": source_name,
                        },
                        "fuente_calculo": (
                            f"ALPHAINVEST_PYTHON_V1:{source_name}"
                        ),
                        "fecha_calculo": calculated_at,
                    }
                )
                for index, point in enumerate(page)
            ],
            total=len(points),
            limit=limit,
            offset=offset,
            indicator_type=indicator_type,
            period=(
                period.strip().upper()
                if period is not None
                else None
            ),
            start_date=start_date,
            end_date=end_date,
        )

    @staticmethod
    def _calculate(
        *,
        prices: list[ClosingPricePoint],
        calculation: IndicatorCalculationSpec,
    ) -> list[CalculatedIndicatorPoint]:
        if (
            calculation.indicator_type
            == FinancialIndicatorType.MACD
        ):
            if (
                calculation.fast_period is None
                or calculation.slow_period is None
                or calculation.signal_period is None
            ):
                raise ValueError(
                    "La configuración MACD está incompleta"
                )

            return calculate_macd(
                prices,
                fast_period=calculation.fast_period,
                slow_period=calculation.slow_period,
                signal_period=calculation.signal_period,
            )

        if calculation.period is None:
            raise ValueError(
                "El periodo del indicador es obligatorio"
            )

        calculators = {
            FinancialIndicatorType.SMA: calculate_sma,
            FinancialIndicatorType.EMA: calculate_ema,
            FinancialIndicatorType.RSI: calculate_rsi,
            FinancialIndicatorType.VOLATILITY: (
                calculate_volatility
            ),
        }

        calculator = calculators.get(
            calculation.indicator_type
        )

        if calculator is None:
            raise ValueError(
                "El indicador solicitado no puede "
                "calcularse directamente"
            )

        return calculator(
            prices,
            period=calculation.period,
        )
    