from datetime import date, timedelta

import exchange_calendars as xcals

from alphainvest.modules.market.domain.trading_calendar_exceptions import (
    InvalidTradingSessionError,
    TradingCalendarRangeError,
    UnsupportedMarketCalendarError,
)


class ExchangeTradingCalendar:
    """Calendario bursátil respaldado por exchange_calendars."""

    MARKET_CALENDARS = {
        "NASDAQ": "XNYS",
    }

    CALENDAR_WINDOW_DAYS = 90

    def target_session(
        self,
        *,
        market_code: str,
        base_date: date,
        horizon_sessions: int,
    ) -> date:
        if horizon_sessions <= 0:
            raise ValueError(
                "horizon_sessions debe ser "
                "mayor que cero"
            )

        normalized_market = (
            market_code.strip().upper()
        )

        calendar_name = (
            self.MARKET_CALENDARS.get(
                normalized_market
            )
        )

        if calendar_name is None:
            raise UnsupportedMarketCalendarError(
                "No existe calendario bursátil "
                f"configurado para {market_code}"
            )

        calendar_start_date = (
            base_date
            - timedelta(days=7)
        )

        end_date = (
            base_date
            + timedelta(
                days=self.CALENDAR_WINDOW_DAYS
            )
        )

        calendar = xcals.get_calendar(
            calendar_name,
            start=calendar_start_date,
            end=end_date,
        )

        base_session = calendar.date_to_session(
            base_date.isoformat(),
            direction="next",
        )

        resolved_base_date = (
            base_session.date()
        )

        if resolved_base_date != base_date:
            raise InvalidTradingSessionError(
                f"{base_date.isoformat()} no es "
                "una sesión bursátil válida "
                f"para {normalized_market}"
            )

        sessions = calendar.sessions_window(
            base_session,
            horizon_sessions + 1,
        )

        if len(sessions) != (
            horizon_sessions + 1
        ):
            raise TradingCalendarRangeError(
                "No fue posible resolver "
                "el horizonte completo"
            )

        target = sessions[-1]

        target_date = date(
            target.year,
            target.month,
            target.day,
        )

        return target_date