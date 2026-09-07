from uuid import uuid4

import pytest

from alphainvest.modules.market.domain.indicator_enums import (
    FinancialIndicatorType,
)
from alphainvest.worker.jobs.market_indicators import (
    build_daily_indicator_request,
)
from alphainvest.worker.registry import (
    WORKER_JOB_REGISTRY,
)

pytestmark = pytest.mark.unit


def test_indicator_job_is_registered() -> None:
    assert (
        "CALCULAR_INDICADORES_DIARIOS"
        in WORKER_JOB_REGISTRY
    )


def test_builds_daily_indicator_request() -> None:
    request = build_daily_indicator_request(
        source_id=uuid4()
    )

    requested_types = {
        calculation.indicator_type
        for calculation in request.calculations
    }

    assert requested_types == {
        FinancialIndicatorType.SMA,
        FinancialIndicatorType.EMA,
        FinancialIndicatorType.RSI,
        FinancialIndicatorType.VOLATILITY,
        FinancialIndicatorType.MACD,
    }

    macd = next(
        calculation
        for calculation in request.calculations
        if (
            calculation.indicator_type
            == FinancialIndicatorType.MACD
        )
    )

    assert macd.fast_period == 12
    assert macd.slow_period == 26
    assert macd.signal_period == 9