from decimal import Decimal, localcontext

from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
)
from alphainvest.modules.market.domain.indicator_values import (
    CalculatedIndicatorPoint,
    ClosingPricePoint,
)

CALCULATION_SOURCE = "ALPHAINVEST_PYTHON_V1"
TRADING_DAYS_PER_YEAR = Decimal("252")
PERCENT_MULTIPLIER = Decimal("100")


def _validate_period(
    *,
    prices: list[ClosingPricePoint],
    period: int,
) -> None:
    if period < 2:
        raise ValueError(
            "El periodo debe ser mayor o igual que 2"
        )

    if len(prices) < period:
        raise ValueError(
            "No existen precios suficientes para el periodo"
        )


def calculate_sma(
    prices: list[ClosingPricePoint],
    *,
    period: int,
) -> list[CalculatedIndicatorPoint]:
    _validate_period(
        prices=prices,
        period=period,
    )

    results: list[CalculatedIndicatorPoint] = []
    period_decimal = Decimal(period)

    for index in range(period - 1, len(prices)):
        window = prices[
            index - period + 1 : index + 1
        ]

        value = (
            sum(
                (price.close for price in window),
                start=Decimal("0"),
            )
            / period_decimal
        )

        results.append(
            CalculatedIndicatorPoint(
                indicator_type=(
                    FinancialIndicatorType.SMA.value
                ),
                date=prices[index].date,
                value=value,
                period=f"{period}D",
                parameters={
                    "period": period,
                    "price_field": "adjusted_close_or_close",
                },
                calculation_source=CALCULATION_SOURCE,
            )
        )

    return results


def calculate_ema(
    prices: list[ClosingPricePoint],
    *,
    period: int,
) -> list[CalculatedIndicatorPoint]:
    _validate_period(
        prices=prices,
        period=period,
    )

    seed_prices = prices[:period]

    seed = (
        sum(
            (price.close for price in seed_prices),
            start=Decimal("0"),
        )
        / Decimal(period)
    )

    multiplier = (
        Decimal("2")
        / Decimal(period + 1)
    )

    results = [
        CalculatedIndicatorPoint(
            indicator_type=(
                FinancialIndicatorType.EMA.value
            ),
            date=prices[period - 1].date,
            value=seed,
            period=f"{period}D",
            parameters={
                "period": period,
                "multiplier": str(multiplier),
                "seed": "SMA",
                "price_field": "adjusted_close_or_close",
            },
            calculation_source=CALCULATION_SOURCE,
        )
    ]

    previous_ema = seed

    for price in prices[period:]:
        current_ema = (
            (price.close - previous_ema)
            * multiplier
            + previous_ema
        )

        results.append(
            CalculatedIndicatorPoint(
                indicator_type=(
                    FinancialIndicatorType.EMA.value
                ),
                date=price.date,
                value=current_ema,
                period=f"{period}D",
                parameters={
                    "period": period,
                    "multiplier": str(multiplier),
                    "seed": "SMA",
                    "price_field": (
                        "adjusted_close_or_close"
                    ),
                },
                calculation_source=CALCULATION_SOURCE,
            )
        )

        previous_ema = current_ema

    return results


def calculate_rsi(
    prices: list[ClosingPricePoint],
    *,
    period: int,
) -> list[CalculatedIndicatorPoint]:
    if period < 2:
        raise ValueError(
            "El periodo debe ser mayor o igual que 2"
        )

    if len(prices) < period + 1:
        raise ValueError(
            "No existen precios suficientes para el RSI"
        )

    changes = [
        prices[index].close
        - prices[index - 1].close
        for index in range(1, len(prices))
    ]

    initial_changes = changes[:period]

    average_gain = (
        sum(
            (
                change
                if change > 0
                else Decimal("0")
                for change in initial_changes
            ),
            start=Decimal("0"),
        )
        / Decimal(period)
    )

    average_loss = (
        sum(
            (
                -change
                if change < 0
                else Decimal("0")
                for change in initial_changes
            ),
            start=Decimal("0"),
        )
        / Decimal(period)
    )

    results: list[CalculatedIndicatorPoint] = []

    def build_rsi() -> Decimal:
        if average_loss == 0:
            return Decimal("100")

        relative_strength = (
            average_gain / average_loss
        )

        return (
            Decimal("100")
            - (
                Decimal("100")
                / (
                    Decimal("1")
                    + relative_strength
                )
            )
        )

    results.append(
        CalculatedIndicatorPoint(
            indicator_type=(
                FinancialIndicatorType.RSI.value
            ),
            date=prices[period].date,
            value=build_rsi(),
            period=f"{period}D",
            parameters={
                "period": period,
                "method": "WILDER",
                "price_field": "adjusted_close_or_close",
            },
            calculation_source=CALCULATION_SOURCE,
        )
    )

    for change_index in range(
        period,
        len(changes),
    ):
        change = changes[change_index]

        gain = (
            change
            if change > 0
            else Decimal("0")
        )
        loss = (
            -change
            if change < 0
            else Decimal("0")
        )

        average_gain = (
            average_gain
            * Decimal(period - 1)
            + gain
        ) / Decimal(period)

        average_loss = (
            average_loss
            * Decimal(period - 1)
            + loss
        ) / Decimal(period)

        results.append(
            CalculatedIndicatorPoint(
                indicator_type=(
                    FinancialIndicatorType.RSI.value
                ),
                date=prices[change_index + 1].date,
                value=build_rsi(),
                period=f"{period}D",
                parameters={
                    "period": period,
                    "method": "WILDER",
                    "price_field": (
                        "adjusted_close_or_close"
                    ),
                },
                calculation_source=CALCULATION_SOURCE,
            )
        )

    return results


def calculate_volatility(
    prices: list[ClosingPricePoint],
    *,
    period: int,
) -> list[CalculatedIndicatorPoint]:
    if period < 2:
        raise ValueError(
            "El periodo debe ser mayor o igual que 2"
        )

    if len(prices) < period + 1:
        raise ValueError(
            "No existen precios suficientes "
            "para calcular volatilidad"
        )

    returns: list[Decimal] = []

    for index in range(1, len(prices)):
        previous_close = prices[index - 1].close

        if previous_close == 0:
            raise ValueError(
                "No puede calcularse un rendimiento "
                "con cierre anterior igual a cero"
            )

        returns.append(
            (
                prices[index].close
                / previous_close
            )
            - Decimal("1")
        )

    results: list[CalculatedIndicatorPoint] = []

    with localcontext() as context:
        context.prec = 40

        annualization_factor = (
            TRADING_DAYS_PER_YEAR.sqrt()
        )

        for return_index in range(
            period - 1,
            len(returns),
        ):
            window = returns[
                return_index - period + 1 :
                return_index + 1
            ]

            mean = (
                sum(
                    window,
                    start=Decimal("0"),
                )
                / Decimal(period)
            )

            variance = (
                sum(
                    (
                        (value - mean) ** 2
                        for value in window
                    ),
                    start=Decimal("0"),
                )
                / Decimal(period - 1)
            )

            value = (
                variance.sqrt()
                * annualization_factor
                * PERCENT_MULTIPLIER
            )

            results.append(
                CalculatedIndicatorPoint(
                    indicator_type=(
                        FinancialIndicatorType
                        .VOLATILITY.value
                    ),
                    date=prices[
                        return_index + 1
                    ].date,
                    value=value,
                    period=f"{period}D",
                    parameters={
                        "period": period,
                        "returns": "SIMPLE",
                        "annualized": True,
                        "trading_days": 252,
                        "unit": "PERCENT",
                        "sample_variance": True,
                        "price_field": (
                            "adjusted_close_or_close"
                        ),
                    },
                    calculation_source=(
                        CALCULATION_SOURCE
                    ),
                )
            )

    return results

def calculate_macd(
    prices: list[ClosingPricePoint],
    *,
    fast_period: int,
    slow_period: int,
    signal_period: int,
) -> list[CalculatedIndicatorPoint]:
    if fast_period < 2:
        raise ValueError(
            "El periodo rápido debe ser mayor o igual que 2"
        )

    if slow_period <= fast_period:
        raise ValueError(
            "El periodo lento debe ser mayor "
            "que el periodo rápido"
        )

    if signal_period < 2:
        raise ValueError(
            "El periodo de señal debe ser mayor "
            "o igual que 2"
        )

    minimum_prices = (
        slow_period
        + signal_period
        - 1
    )

    if len(prices) < minimum_prices:
        raise ValueError(
            "No existen precios suficientes para MACD"
        )

    fast_ema_points = calculate_ema(
        prices,
        period=fast_period,
    )
    slow_ema_points = calculate_ema(
        prices,
        period=slow_period,
    )

    fast_ema_by_date = {
        point.date: point.value
        for point in fast_ema_points
    }

    macd_values: list[
        tuple[ClosingPricePoint, Decimal]
    ] = []

    price_by_date = {
        price.date: price
        for price in prices
    }

    for slow_point in slow_ema_points:
        fast_value = fast_ema_by_date.get(
            slow_point.date
        )

        if fast_value is None:
            continue

        price = price_by_date[slow_point.date]

        macd_values.append(
            (
                price,
                fast_value - slow_point.value,
            )
        )

    if len(macd_values) < signal_period:
        raise ValueError(
            "No existen valores MACD suficientes "
            "para calcular la señal"
        )

    period_label = (
        f"{fast_period}-"
        f"{slow_period}-"
        f"{signal_period}"
    )

    common_parameters = {
        "fast_period": fast_period,
        "slow_period": slow_period,
        "signal_period": signal_period,
        "ema_seed": "SMA",
        "price_field": "adjusted_close_or_close",
    }

    results: list[CalculatedIndicatorPoint] = []

    for price, macd_value in macd_values:
        results.append(
            CalculatedIndicatorPoint(
                indicator_type=(
                    FinancialIndicatorType.MACD.value
                ),
                date=price.date,
                value=macd_value,
                period=period_label,
                parameters={
                    **common_parameters,
                    "series": "MACD",
                },
                calculation_source=CALCULATION_SOURCE,
            )
        )

    signal_seed = (
        sum(
            (
                value
                for _, value
                in macd_values[:signal_period]
            ),
            start=Decimal("0"),
        )
        / Decimal(signal_period)
    )

    signal_multiplier = (
        Decimal("2")
        / Decimal(signal_period + 1)
    )

    previous_signal = signal_seed

    first_signal_index = signal_period - 1
    first_price, first_macd = macd_values[
        first_signal_index
    ]

    results.append(
        CalculatedIndicatorPoint(
            indicator_type=(
                FinancialIndicatorType
                .MACD_SIGNAL.value
            ),
            date=first_price.date,
            value=signal_seed,
            period=period_label,
            parameters={
                **common_parameters,
                "series": "SIGNAL",
                "signal_multiplier": str(
                    signal_multiplier
                ),
            },
            calculation_source=CALCULATION_SOURCE,
        )
    )

    results.append(
        CalculatedIndicatorPoint(
            indicator_type=(
                FinancialIndicatorType
                .MACD_HISTOGRAM.value
            ),
            date=first_price.date,
            value=first_macd - signal_seed,
            period=period_label,
            parameters={
                **common_parameters,
                "series": "HISTOGRAM",
            },
            calculation_source=CALCULATION_SOURCE,
        )
    )

    for price, macd_value in macd_values[
        signal_period:
    ]:
        current_signal = (
            (macd_value - previous_signal)
            * signal_multiplier
            + previous_signal
        )

        results.append(
            CalculatedIndicatorPoint(
                indicator_type=(
                    FinancialIndicatorType
                    .MACD_SIGNAL.value
                ),
                date=price.date,
                value=current_signal,
                period=period_label,
                parameters={
                    **common_parameters,
                    "series": "SIGNAL",
                    "signal_multiplier": str(
                        signal_multiplier
                    ),
                },
                calculation_source=CALCULATION_SOURCE,
            )
        )

        results.append(
            CalculatedIndicatorPoint(
                indicator_type=(
                    FinancialIndicatorType
                    .MACD_HISTOGRAM.value
                ),
                date=price.date,
                value=(
                    macd_value - current_signal
                ),
                period=period_label,
                parameters={
                    **common_parameters,
                    "series": "HISTOGRAM",
                },
                calculation_source=CALCULATION_SOURCE,
            )
        )

        previous_signal = current_signal

    return results