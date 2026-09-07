from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any


@dataclass(frozen=True, slots=True)
class ClosingPricePoint:
    date: date
    close: Decimal


@dataclass(frozen=True, slots=True)
class CalculatedIndicatorPoint:
    indicator_type: str
    date: date
    value: Decimal
    period: str
    parameters: dict[str, Any]
    calculation_source: str