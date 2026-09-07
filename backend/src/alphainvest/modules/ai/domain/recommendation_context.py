from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class RecommendationPredictionSignal:
    """Señal proveniente de una predicción de activo."""

    prediction_id: UUID
    asset_id: UUID
    base_date: date
    target_date: date
    horizon: str
    base_price: Decimal
    predicted_price: Decimal
    expected_return_percentage: Decimal | None
    trend: str
    confidence: Decimal
    bullish_probability: Decimal | None
    neutral_probability: Decimal | None
    bearish_probability: Decimal | None


@dataclass(frozen=True, slots=True)
class RecommendationIndicatorSignal:
    """Indicador técnico utilizado como evidencia."""

    indicator_type: str
    period: str
    value: Decimal
    date: date


@dataclass(frozen=True, slots=True)
class RecommendationRiskProfileSignal:
    """Perfil de riesgo vigente del usuario."""

    profile_id: UUID
    classification: str
    score: Decimal
    confidence: Decimal | None


@dataclass(frozen=True, slots=True)
class RecommendationPositionSignal:
    """Posición existente del activo dentro del portafolio."""

    position_id: UUID
    quantity: Decimal
    average_purchase_price: Decimal
    total_cost: Decimal
    current_price: Decimal | None
    current_value: Decimal | None
    profit_loss: Decimal | None
    return_percentage: Decimal | None
    status: str


@dataclass(frozen=True, slots=True)
class RecommendationPortfolioSignal:
    """Contexto financiero del portafolio del usuario."""

    portfolio_id: UUID
    initial_capital: Decimal
    cash_balance: Decimal
    status: str
    position: RecommendationPositionSignal | None


@dataclass(frozen=True, slots=True)
class RecommendationContext:
    """Información normalizada consumida por el motor."""

    request_id: UUID
    user_id: UUID
    asset_id: UUID
    model_version_id: UUID
    horizon: str

    prediction: RecommendationPredictionSignal

    latest_price: Decimal | None

    indicators: tuple[
        RecommendationIndicatorSignal,
        ...,
    ]

    risk_profile: (
        RecommendationRiskProfileSignal
        | None
    )

    portfolio: (
        RecommendationPortfolioSignal
        | None
    )