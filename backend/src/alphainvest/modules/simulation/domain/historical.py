from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from alphainvest.modules.simulation.domain.enums import (
    ContributionFrequency,
)


@dataclass(frozen=True, slots=True)
class HistoricalPricePoint:
    """Precio de cierre normalizado usado por el simulador."""

    date: date
    price: Decimal

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError(
                "El precio histórico debe ser mayor que cero"
            )


@dataclass(frozen=True, slots=True)
class HistoricalAssetInput:
    """Activo y distribución utilizados por el motor histórico."""

    asset_id: UUID
    assigned_percentage: Decimal
    prices: tuple[HistoricalPricePoint, ...]

    def __post_init__(self) -> None:
        if not (
            Decimal("0")
            < self.assigned_percentage
            <= Decimal("100")
        ):
            raise ValueError(
                "El porcentaje asignado debe ser "
                "mayor que cero y menor o igual a 100"
            )

        if not self.prices:
            raise ValueError(
                "El activo debe contener precios históricos"
            )

        dates = [
            point.date
            for point in self.prices
        ]

        if dates != sorted(dates):
            raise ValueError(
                "Los precios históricos deben estar "
                "ordenados cronológicamente"
            )

        if len(dates) != len(set(dates)):
            raise ValueError(
                "No puede haber precios históricos "
                "duplicados para la misma fecha"
            )


@dataclass(frozen=True, slots=True)
class HistoricalSimulationInput:
    """Datos normalizados de entrada para una simulación histórica."""

    initial_capital: Decimal
    currency: str
    requested_start_date: date
    requested_end_date: date
    assets: tuple[HistoricalAssetInput, ...]
    periodic_contribution: Decimal = Decimal("0")
    contribution_frequency: ContributionFrequency | None = None
    commission_percentage: Decimal = Decimal("0")
    risk_free_rate: Decimal | None = None

    def __post_init__(self) -> None:
        normalized_currency = (
            self.currency.strip().upper()
        )

        if self.initial_capital <= 0:
            raise ValueError(
                "El capital inicial debe ser mayor que cero"
            )

        if len(normalized_currency) != 3:
            raise ValueError(
                "La moneda debe contener tres caracteres"
            )

        if not normalized_currency.isalpha():
            raise ValueError(
                "La moneda debe contener únicamente letras"
            )

        if (
            self.requested_end_date
            <= self.requested_start_date
        ):
            raise ValueError(
                "La fecha final debe ser posterior "
                "a la fecha inicial"
            )

        if not self.assets:
            raise ValueError(
                "La simulación debe contener "
                "al menos un activo"
            )

        asset_ids = [
            asset.asset_id
            for asset in self.assets
        ]

        if len(asset_ids) != len(set(asset_ids)):
            raise ValueError(
                "Un activo no puede repetirse "
                "dentro de la simulación"
            )

        total_percentage = sum(
            (
                asset.assigned_percentage
                for asset in self.assets
            ),
            start=Decimal("0"),
        )

        if total_percentage != Decimal("100"):
            raise ValueError(
                "Los porcentajes de los activos "
                "deben sumar 100"
            )

        if self.periodic_contribution < 0:
            raise ValueError(
                "La aportación periódica no puede ser negativa"
            )

        if (
            self.periodic_contribution == 0
            and self.contribution_frequency is not None
        ):
            raise ValueError(
                "No debe existir frecuencia cuando "
                "la aportación periódica es cero"
            )

        if (
            self.periodic_contribution > 0
            and self.contribution_frequency is None
        ):
            raise ValueError(
                "Debe existir frecuencia cuando "
                "hay aportación periódica"
            )

        if not (
            Decimal("0")
            <= self.commission_percentage
            <= Decimal("100")
        ):
            raise ValueError(
                "La comisión debe estar entre 0 y 100"
            )

        if (
            self.risk_free_rate is not None
            and self.risk_free_rate <= Decimal("-100")
        ):
            raise ValueError(
                "La tasa libre de riesgo "
                "debe ser mayor que -100"
            )

        object.__setattr__(
            self,
            "currency",
            normalized_currency,
        )


@dataclass(frozen=True, slots=True)
class HistoricalAlignedAsset:
    """Serie histórica de un activo limitada al calendario común."""

    asset_id: UUID
    assigned_percentage: Decimal
    prices: tuple[HistoricalPricePoint, ...]

    def __post_init__(self) -> None:
        if not self.prices:
            raise ValueError(
                "El activo alineado debe contener precios"
            )


@dataclass(frozen=True, slots=True)
class HistoricalAlignedSimulation:
    """Periodo efectivo y series comunes de la simulación."""

    initial_capital: Decimal
    currency: str
    requested_start_date: date
    requested_end_date: date
    effective_start_date: date
    effective_end_date: date
    common_dates: tuple[date, ...]
    assets: tuple[HistoricalAlignedAsset, ...]
    periodic_contribution: Decimal = Decimal("0")
    contribution_frequency: ContributionFrequency | None = None
    commission_percentage: Decimal = Decimal("0")
    risk_free_rate: Decimal | None = None

    def __post_init__(self) -> None:
        normalized_currency = (
            self.currency.strip().upper()
        )

        if self.initial_capital <= 0:
            raise ValueError(
                "El capital inicial debe ser mayor que cero"
            )

        if (
            len(normalized_currency) != 3
            or not normalized_currency.isalpha()
        ):
            raise ValueError(
                "La moneda debe contener tres letras"
            )

        if self.periodic_contribution < 0:
            raise ValueError(
                "La aportación periódica no puede ser negativa"
            )

        if (
            self.periodic_contribution == 0
            and self.contribution_frequency is not None
        ):
            raise ValueError(
                "No debe existir frecuencia cuando "
                "la aportación periódica es cero"
            )

        if (
            self.periodic_contribution > 0
            and self.contribution_frequency is None
        ):
            raise ValueError(
                "Debe existir frecuencia cuando "
                "hay aportación periódica"
            )

        if not (
            Decimal("0")
            <= self.commission_percentage
            <= Decimal("100")
        ):
            raise ValueError(
                "La comisión debe estar entre 0 y 100"
            )

        if (
            self.risk_free_rate is not None
            and self.risk_free_rate <= Decimal("-100")
        ):
            raise ValueError(
                "La tasa libre de riesgo "
                "debe ser mayor que -100"
            )

        object.__setattr__(
            self,
            "currency",
            normalized_currency,
        )
        if (
            self.effective_start_date
            > self.effective_end_date
        ):
            raise ValueError(
                "La fecha inicial efectiva no puede "
                "ser posterior a la fecha final efectiva"
            )

        if not self.common_dates:
            raise ValueError(
                "La simulación no tiene fechas comunes"
            )

        if (
            self.common_dates[0]
            != self.effective_start_date
        ):
            raise ValueError(
                "La primera fecha común debe coincidir "
                "con la fecha inicial efectiva"
            )

        if (
            self.common_dates[-1]
            != self.effective_end_date
        ):
            raise ValueError(
                "La última fecha común debe coincidir "
                "con la fecha final efectiva"
            )

        if tuple(sorted(self.common_dates)) != (
            self.common_dates
        ):
            raise ValueError(
                "Las fechas comunes deben estar "
                "ordenadas cronológicamente"
            )

        if len(self.common_dates) != len(
            set(self.common_dates)
        ):
            raise ValueError(
                "Las fechas comunes no pueden repetirse"
            )

        if not self.assets:
            raise ValueError(
                "La simulación alineada debe contener "
                "al menos un activo"
            )

        expected_dates = self.common_dates

        for asset in self.assets:
            asset_dates = tuple(
                point.date
                for point in asset.prices
            )

            if asset_dates != expected_dates:
                raise ValueError(
                    "Todos los activos deben utilizar "
                    "el mismo calendario histórico"
                )


@dataclass(frozen=True, slots=True)
class HistoricalInitialPosition:
    """Posición virtual adquirida al inicio efectivo."""

    asset_id: UUID
    assigned_percentage: Decimal
    allocated_capital: Decimal
    initial_price: Decimal
    initial_quantity: Decimal
    commission_amount: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.allocated_capital <= 0:
            raise ValueError(
                "El capital asignado debe ser mayor que cero"
            )

        if self.initial_price <= 0:
            raise ValueError(
                "El precio inicial debe ser mayor que cero"
            )

        if self.initial_quantity <= 0:
            raise ValueError(
                "La cantidad inicial debe ser mayor que cero"
            )

        if self.commission_amount < 0:
            raise ValueError(
                "La comisión inicial no puede ser negativa"
            )

        if self.commission_amount >= self.allocated_capital:
            raise ValueError(
                "La comisión inicial debe ser menor "
                "al capital asignado"
            )


@dataclass(frozen=True, slots=True)
class HistoricalInitialPortfolio:
    """Resultado de la compra virtual inicial."""

    initial_capital: Decimal
    currency: str
    effective_start_date: date
    positions: tuple[HistoricalInitialPosition, ...]
    total_commission: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError(
                "El capital inicial debe ser mayor que cero"
            )

        if not self.positions:
            raise ValueError(
                "El portafolio inicial debe contener posiciones"
            )

        allocated_total = sum(
            (
                position.allocated_capital
                for position in self.positions
            ),
            start=Decimal("0"),
        )

        if allocated_total != self.initial_capital:
            raise ValueError(
                "El capital asignado debe coincidir "
                "con el capital inicial"
            )

        calculated_commission = sum(
            (
                position.commission_amount
                for position in self.positions
            ),
            start=Decimal("0"),
        )

        if calculated_commission != self.total_commission:
            raise ValueError(
                "La comisión total inicial debe coincidir "
                "con la suma de las posiciones"
            )


@dataclass(frozen=True, slots=True)
class HistoricalPositionValue:
    """Valor de una posición virtual en una fecha."""

    asset_id: UUID
    price: Decimal
    quantity: Decimal
    value: Decimal

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError(
                "El precio de valoración debe ser mayor que cero"
            )

        if self.quantity <= 0:
            raise ValueError(
                "La cantidad virtual debe ser mayor que cero"
            )

        if self.value <= 0:
            raise ValueError(
                "El valor de la posición debe ser mayor que cero"
            )


@dataclass(frozen=True, slots=True)
class HistoricalPortfolioPoint:
    """Valor consolidado del portafolio en una fecha."""

    date: date
    total_value: Decimal
    positions: tuple[HistoricalPositionValue, ...]
    contribution_amount: Decimal = Decimal("0")
    commission_amount: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if self.total_value <= 0:
            raise ValueError(
                "El valor total del portafolio "
                "debe ser mayor que cero"
            )

        if not self.positions:
            raise ValueError(
                "El punto histórico debe contener posiciones"
            )

        calculated_total = sum(
            (
                position.value
                for position in self.positions
            ),
            start=Decimal("0"),
        )

        if calculated_total != self.total_value:
            raise ValueError(
                "El valor total debe coincidir "
                "con la suma de las posiciones"
            )

        if self.contribution_amount < 0:
            raise ValueError(
                "La aportación no puede ser negativa"
            )

        if self.commission_amount < 0:
            raise ValueError(
                "La comisión no puede ser negativa"
            )


@dataclass(frozen=True, slots=True)
class HistoricalPortfolioEvolution:
    """Serie histórica valorizada del portafolio."""

    initial_capital: Decimal
    currency: str
    points: tuple[HistoricalPortfolioPoint, ...]

    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError(
                "El capital inicial debe ser mayor que cero"
            )

        if not self.points:
            raise ValueError(
                "La evolución histórica debe contener puntos"
            )

        dates = tuple(
            point.date
            for point in self.points
        )

        if dates != tuple(sorted(dates)):
            raise ValueError(
                "La evolución debe estar "
                "ordenada cronológicamente"
            )

        if len(dates) != len(set(dates)):
            raise ValueError(
                "La evolución no puede contener "
                "fechas duplicadas"
            )


@dataclass(frozen=True, slots=True)
class HistoricalContributionPurchase:
    """Compra realizada con una aportación periódica."""

    asset_id: UUID
    gross_amount: Decimal
    net_invested_amount: Decimal
    commission_amount: Decimal
    price: Decimal
    quantity_acquired: Decimal

    def __post_init__(self) -> None:
        if self.gross_amount <= 0:
            raise ValueError(
                "El monto bruto debe ser mayor que cero"
            )

        if self.net_invested_amount <= 0:
            raise ValueError(
                "El monto neto invertido debe ser mayor que cero"
            )

        if self.commission_amount < 0:
            raise ValueError(
                "La comisión no puede ser negativa"
            )

        if (
            self.net_invested_amount
            + self.commission_amount
            != self.gross_amount
        ):
            raise ValueError(
                "La inversión neta más la comisión "
                "debe coincidir con el monto bruto"
            )

        if self.price <= 0:
            raise ValueError(
                "El precio de compra debe ser mayor que cero"
            )

        if self.quantity_acquired <= 0:
            raise ValueError(
                "La cantidad adquirida debe ser mayor que cero"
            )


@dataclass(frozen=True, slots=True)
class HistoricalContributionEvent:
    """Aportación periódica ejecutada en una fecha común."""

    target_date: date
    execution_date: date
    gross_amount: Decimal
    commission_amount: Decimal
    purchases: tuple[HistoricalContributionPurchase, ...]

    def __post_init__(self) -> None:
        if self.execution_date < self.target_date:
            raise ValueError(
                "La aportación no puede ejecutarse "
                "antes de su fecha objetivo"
            )

        if self.gross_amount <= 0:
            raise ValueError(
                "La aportación debe ser mayor que cero"
            )

        if not self.purchases:
            raise ValueError(
                "La aportación debe contener compras"
            )

        purchase_total = sum(
            (
                purchase.gross_amount
                for purchase in self.purchases
            ),
            start=Decimal("0"),
        )

        if purchase_total != self.gross_amount:
            raise ValueError(
                "Las compras deben consumir "
                "la aportación completa"
            )

        calculated_commission = sum(
            (
                purchase.commission_amount
                for purchase in self.purchases
            ),
            start=Decimal("0"),
        )

        if calculated_commission != self.commission_amount:
            raise ValueError(
                "La comisión del evento debe coincidir "
                "con las compras"
            )


@dataclass(frozen=True, slots=True)
class HistoricalContributionPlan:
    """Plan completo de aportaciones ejecutables."""

    events: tuple[HistoricalContributionEvent, ...]
    total_contributions: Decimal
    total_commissions: Decimal

    def __post_init__(self) -> None:
        if self.total_contributions < 0:
            raise ValueError(
                "Las aportaciones totales no pueden ser negativas"
            )

        if self.total_commissions < 0:
            raise ValueError(
                "Las comisiones totales no pueden ser negativas"
            )

        calculated_contributions = sum(
            (
                event.gross_amount
                for event in self.events
            ),
            start=Decimal("0"),
        )

        calculated_commissions = sum(
            (
                event.commission_amount
                for event in self.events
            ),
            start=Decimal("0"),
        )

        if calculated_contributions != self.total_contributions:
            raise ValueError(
                "Las aportaciones totales no coinciden "
                "con los eventos"
            )

        if calculated_commissions != self.total_commissions:
            raise ValueError(
                "Las comisiones totales no coinciden "
                "con los eventos"
            )


@dataclass(frozen=True, slots=True)
class HistoricalMetricsResult:
    """Métricas financieras consolidadas del backtest."""

    daily_returns: tuple[Decimal, ...]
    total_return_percentage: Decimal
    annualized_return_percentage: Decimal | None
    annualized_volatility_percentage: Decimal | None
    sharpe_ratio: Decimal | None
    maximum_drawdown_percentage: Decimal
    value_at_risk: Decimal | None
    value_at_risk_confidence: Decimal | None

    def __post_init__(self) -> None:
        if (
            self.annualized_volatility_percentage is not None
            and self.annualized_volatility_percentage < 0
        ):
            raise ValueError(
                "La volatilidad anualizada "
                "no puede ser negativa"
            )

        if not (
            Decimal("0")
            <= self.maximum_drawdown_percentage
            <= Decimal("100")
        ):
            raise ValueError(
                "El máximo drawdown debe estar "
                "entre 0 y 100"
            )

        if (
            self.value_at_risk is not None
            and self.value_at_risk < 0
        ):
            raise ValueError(
                "El valor en riesgo no puede ser negativo"
            )

        if (
            self.value_at_risk_confidence is not None
            and not (
                Decimal("0")
                <= self.value_at_risk_confidence
                <= Decimal("1")
            )
        ):
            raise ValueError(
                "El nivel de confianza VaR debe estar "
                "entre 0 y 1"
            )


@dataclass(frozen=True, slots=True)
class HistoricalSimulationResult:
    """Resultado consolidado de una simulación histórica."""

    initial_capital: Decimal
    total_contributions: Decimal
    final_capital: Decimal
    profit_loss: Decimal
    total_commissions: Decimal
    currency: str
    effective_start_date: date
    effective_end_date: date
    initial_portfolio: HistoricalInitialPortfolio
    contribution_plan: HistoricalContributionPlan
    evolution: HistoricalPortfolioEvolution
    metrics: HistoricalMetricsResult

    def __post_init__(self) -> None:
        normalized_currency = (
            self.currency.strip().upper()
        )

        if self.initial_capital <= 0:
            raise ValueError(
                "El capital inicial debe ser mayor que cero"
            )

        if self.total_contributions < 0:
            raise ValueError(
                "Las aportaciones totales "
                "no pueden ser negativas"
            )

        if self.final_capital < 0:
            raise ValueError(
                "El capital final no puede ser negativo"
            )

        if self.total_commissions < 0:
            raise ValueError(
                "Las comisiones totales "
                "no pueden ser negativas"
            )

        if (
            self.effective_end_date
            < self.effective_start_date
        ):
            raise ValueError(
                "La fecha final efectiva no puede ser "
                "anterior a la fecha inicial efectiva"
            )

        if (
            len(normalized_currency) != 3
            or not normalized_currency.isalpha()
        ):
            raise ValueError(
                "La moneda debe contener tres letras"
            )

        expected_profit_loss = (
            self.final_capital
            - self.initial_capital
            - self.total_contributions
        )

        if self.profit_loss != expected_profit_loss:
            raise ValueError(
                "La ganancia o pérdida no coincide "
                "con los capitales de la simulación"
            )

        expected_commissions = (
            self.initial_portfolio.total_commission
            + self.contribution_plan.total_commissions
        )

        if self.total_commissions != expected_commissions:
            raise ValueError(
                "Las comisiones totales no coinciden "
                "con las operaciones simuladas"
            )

        if (
            self.evolution.points[-1].total_value
            != self.final_capital
        ):
            raise ValueError(
                "El capital final debe coincidir "
                "con la última valoración"
            )

        object.__setattr__(
            self,
            "currency",
            normalized_currency,
        )


@dataclass(frozen=True, slots=True)
class HistoricalAssetResult:
    """Resultado consolidado individual de un activo."""

    asset_id: UUID
    assigned_percentage: Decimal
    allocated_capital: Decimal
    initial_quantity: Decimal
    initial_price: Decimal
    final_price: Decimal
    final_value: Decimal
    profit_loss: Decimal
    return_percentage: Decimal
    volatility_percentage: Decimal | None
    maximum_drawdown_percentage: Decimal | None
    total_contributions: Decimal
    final_quantity: Decimal

    def __post_init__(self) -> None:
        if not (
            Decimal("0")
            < self.assigned_percentage
            <= Decimal("100")
        ):
            raise ValueError(
                "El porcentaje asignado debe estar "
                "entre 0 y 100"
            )

        if self.allocated_capital < 0:
            raise ValueError(
                "El capital asignado no puede ser negativo"
            )

        if self.initial_quantity < 0:
            raise ValueError(
                "La cantidad inicial no puede ser negativa"
            )

        if self.final_quantity < 0:
            raise ValueError(
                "La cantidad final no puede ser negativa"
            )

        if self.initial_price < 0:
            raise ValueError(
                "El precio inicial no puede ser negativo"
            )

        if self.final_price < 0:
            raise ValueError(
                "El precio final no puede ser negativo"
            )

        if self.final_value < 0:
            raise ValueError(
                "El valor final no puede ser negativo"
            )

        if (
            self.volatility_percentage is not None
            and self.volatility_percentage < 0
        ):
            raise ValueError(
                "La volatilidad no puede ser negativa"
            )

        if (
            self.maximum_drawdown_percentage is not None
            and not (
                Decimal("0")
                <= self.maximum_drawdown_percentage
                <= Decimal("100")
            )
        ):
            raise ValueError(
                "El máximo drawdown debe estar "
                "entre 0 y 100"
            )

        if self.total_contributions < 0:
            raise ValueError(
                "Las aportaciones no pueden ser negativas"
            )