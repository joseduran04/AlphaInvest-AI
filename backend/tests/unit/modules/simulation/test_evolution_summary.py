from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest

from alphainvest.modules.simulation.application.evolution_summary import (
    build_evolution_summary,
)

pytestmark = pytest.mark.unit


def build_evolution(values: list[str], contributions: list[str] | None = None):
    contributions = contributions or ["0"] * len(values)
    start = date(2026, 9, 1)

    return SimpleNamespace(
        initial_capital=Decimal("10000"),
        points=tuple(
            SimpleNamespace(
                date=start + timedelta(days=index),
                total_value=Decimal(value),
                contribution_amount=Decimal(contribution),
            )
            for index, (value, contribution) in enumerate(
                zip(values, contributions, strict=True)
            )
        ),
    )


def test_series_tracks_value_and_accumulated_contributions() -> None:
    series = build_evolution_summary(
        build_evolution(
            ["10000", "10100", "10600"],
            ["0", "0", "500"],
        )  # type: ignore[arg-type]
    )

    assert series == [
        {"fecha": "2026-09-01", "valor": "10000", "aportado": "10000"},
        {"fecha": "2026-09-02", "valor": "10100", "aportado": "10000"},
        {"fecha": "2026-09-03", "valor": "10600", "aportado": "10500"},
    ]


def test_long_series_is_downsampled_keeping_first_and_last() -> None:
    values = [str(10000 + index) for index in range(2000)]

    series = build_evolution_summary(
        build_evolution(values),  # type: ignore[arg-type]
        max_points=100,
    )

    assert len(series) <= 101
    assert series[0]["valor"] == "10000"
    assert series[-1]["valor"] == "11999"
    assert [point["fecha"] for point in series] == sorted(
        point["fecha"] for point in series
    )


def test_empty_evolution() -> None:
    assert build_evolution_summary(
        SimpleNamespace(initial_capital=Decimal("1"), points=())  # type: ignore[arg-type]
    ) == []
