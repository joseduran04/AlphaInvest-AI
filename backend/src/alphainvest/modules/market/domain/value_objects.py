from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class DailyPricePoint:
    """Precio diario normalizado proveniente de un proveedor."""

    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adjusted_close: Decimal | None
    volume: Decimal
    currency: str

    def __post_init__(self) -> None:
        normalized_currency = self.currency.strip().upper()

        if len(normalized_currency) != 3:
            raise ValueError(
                "La moneda debe contener tres caracteres"
            )

        if any(
            value < 0
            for value in (
                self.open,
                self.high,
                self.low,
                self.close,
                self.volume,
            )
        ):
            raise ValueError(
                "Los precios y el volumen no pueden ser negativos"
            )

        if self.high < self.low:
            raise ValueError(
                "El precio máximo no puede ser menor al mínimo"
            )

        if not self.low <= self.open <= self.high:
            raise ValueError(
                "La apertura debe estar entre mínimo y máximo"
            )

        if not self.low <= self.close <= self.high:
            raise ValueError(
                "El cierre debe estar entre mínimo y máximo"
            )

        object.__setattr__(
            self,
            "currency",
            normalized_currency,
        )