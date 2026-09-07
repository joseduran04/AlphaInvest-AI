from dataclasses import replace
from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError

from alphainvest.modules.market.domain.exceptions import (
    AssetNotFoundError,
    FinancialSourceNotFoundError,
    IndicatorCalculationError,
    InsufficientPriceHistoryError,
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
    IndicatorCalculationItemResponse,
    IndicatorCalculationRequest,
    IndicatorCalculationResponse,
    IndicatorCalculationSpec,
)


class FinancialIndicatorService:
    """Calcula, persiste y consulta indicadores financieros."""

    def __init__(
        self,
        repository: MarketRepository,
    ) -> None:
        self._repository = repository

    async def calculate_indicators(
        self,
        *,
        asset_id: UUID,
        request: IndicatorCalculationRequest,
    ) -> IndicatorCalculationResponse:
        asset = await self._repository.get_asset(
            asset_id
        )

        if asset is None:
            raise AssetNotFoundError(
                "El activo solicitado no existe"
            )

        source = (
            await self._repository.get_financial_source(
                request.source_id
            )
        )

        if source is None:
            raise FinancialSourceNotFoundError(
                "La fuente financiera no existe"
            )

        if not source.activa:
            raise FinancialSourceNotFoundError(
                "La fuente financiera no está activa"
            )

        prices = (
            await self._repository
            .list_closing_prices_for_indicators(
                asset_id=asset.id,
                source_id=source.id,
            )
        )

        if not prices:
            raise InsufficientPriceHistoryError(
                "El activo no tiene precios para la fuente "
                "seleccionada"
            )

        all_indicators: list[
            CalculatedIndicatorPoint
        ] = []

        for calculation in request.calculations:
            try:
                calculated = self._calculate(
                    prices=prices,
                    calculation=calculation,
                )
            except ValueError as error:
                raise InsufficientPriceHistoryError(
                    str(error)
                ) from error

            enriched = [
                replace(
                    indicator,
                    parameters={
                        **indicator.parameters,
                        "price_source_id": str(source.id),
                        "price_source_name": source.nombre,
                    },
                    calculation_source=(
                        "ALPHAINVEST_PYTHON_V1:"
                        f"{source.nombre}"
                    ),
                )
                for indicator in calculated
            ]

            
            all_indicators.extend(enriched)

        keys = [
            (
                indicator.indicator_type,
                indicator.date,
                indicator.period,
            )
            for indicator in all_indicators
        ]

        existing_keys = (
            await self._repository
            .get_existing_indicator_keys(
                asset_id=asset.id,
                keys=keys,
            )
        )

        try:
            await self._repository.upsert_financial_indicators(
                asset_id=asset.id,
                indicators=all_indicators,
            )

            await self._repository.commit()

        except SQLAlchemyError as error:
            await self._repository.rollback()

            raise IndicatorCalculationError(
                "No fue posible guardar los indicadores"
            ) from error

        grouped_indicators: dict[
            tuple[str, str],
            list[CalculatedIndicatorPoint],
        ] = {}

        for indicator in all_indicators:
            group_key = (
                indicator.indicator_type,
                indicator.period,
            )

            grouped_indicators.setdefault(
                group_key,
                [],
            ).append(indicator)

        response_items: list[
            IndicatorCalculationItemResponse
        ] = []

        for (
            indicator_type_value,
            period,
        ), indicators in grouped_indicators.items():
            group_keys = {
                (
                    indicator.indicator_type,
                    indicator.date,
                    indicator.period,
                )
                for indicator in indicators
            }

            updated = len(
                group_keys.intersection(existing_keys)
            )
            created = len(group_keys) - updated

            response_items.append(
                IndicatorCalculationItemResponse(
                    indicator_type=(
                        FinancialIndicatorType(
                            indicator_type_value
                        )
                    ),
                    period=period,
                    calculated=len(indicators),
                    created=created,
                    updated=updated,
                    first_date=indicators[0].date,
                    last_date=indicators[-1].date,
                )
            )

        return IndicatorCalculationResponse(
            asset_id=asset.id,
            symbol=asset.simbolo,
            source_id=source.id,
            source_name=source.nombre,
            total_calculated=len(all_indicators),
            total_created=sum(
                item.created
                for item in response_items
            ),
            total_updated=sum(
                item.updated
                for item in response_items
            ),
            items=response_items,
            calculated_at=datetime.now(UTC),
        )

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

        indicators, total = (
            await self._repository
            .list_financial_indicators(
                asset_id=asset.id,
                indicator_type=(
                    indicator_type.value
                    if indicator_type is not None
                    else None
                ),
                period=period,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=offset,
            )
        )

        return FinancialIndicatorListResponse(
            asset_id=asset.id,
            items=[
                FinancialIndicatorResponse.model_validate(
                    indicator
                )
                for indicator in indicators
            ],
            total=total,
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
    