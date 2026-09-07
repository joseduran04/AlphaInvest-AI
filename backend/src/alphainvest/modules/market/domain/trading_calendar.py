from datetime import date
from typing import Protocol


class TradingCalendar(Protocol):
    """Contrato para resolver sesiones bursátiles."""

    def target_session(
        self,
        *,
        market_code: str,
        base_date: date,
        horizon_sessions: int,
    ) -> date:
        """Obtiene la sesión objetivo futura."""
        ...