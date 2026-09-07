from datetime import date
from decimal import Decimal
from uuid import uuid4

from alphainvest.modules.ai.domain.recommendation_context import (
    RecommendationContext,
    RecommendationPortfolioSignal,
    RecommendationPositionSignal,
    RecommendationPredictionSignal,
    RecommendationRiskProfileSignal,
)
from alphainvest.modules.ai.domain.recommendation_engine import (
    RecommendationEngine,
)
from alphainvest.modules.ai.domain.recommendation_enums import (
    RecommendationAssetAction,
    RecommendationRiskLevel,
    RecommendationType,
)


def build_context(
    *,
    trend: str,
    confidence: str,
    expected_return: str | None,
    classification: str = "MODERADO",
    with_position: bool = False,
) -> RecommendationContext:
    asset_id = uuid4()

    prediction = RecommendationPredictionSignal(
        prediction_id=uuid4(),
        asset_id=asset_id,
        base_date=date(2026, 8, 27),
        target_date=date(2026, 8, 28),
        horizon="CORTO_PLAZO",
        base_price=Decimal("100"),
        predicted_price=Decimal("105"),
        expected_return_percentage=(
            Decimal(expected_return)
            if expected_return is not None
            else None
        ),
        trend=trend,
        confidence=Decimal(confidence),
        bullish_probability=None,
        neutral_probability=None,
        bearish_probability=None,
    )

    profile = RecommendationRiskProfileSignal(
        profile_id=uuid4(),
        classification=classification,
        score=Decimal("50"),
        confidence=Decimal("0.90"),
    )

    portfolio = None

    if with_position:
        position = RecommendationPositionSignal(
            position_id=uuid4(),
            quantity=Decimal("10"),
            average_purchase_price=Decimal("95"),
            total_cost=Decimal("950"),
            current_price=Decimal("100"),
            current_value=Decimal("1000"),
            profit_loss=Decimal("50"),
            return_percentage=Decimal("5"),
            status="ABIERTA",
        )

        portfolio = RecommendationPortfolioSignal(
            portfolio_id=uuid4(),
            initial_capital=Decimal("10000"),
            cash_balance=Decimal("5000"),
            status="ACTIVO",
            position=position,
        )

    return RecommendationContext(
        request_id=uuid4(),
        user_id=uuid4(),
        asset_id=asset_id,
        model_version_id=uuid4(),
        horizon="CORTO_PLAZO",
        prediction=prediction,
        latest_price=Decimal("100"),
        indicators=(),
        risk_profile=profile,
        portfolio=portfolio,
    )


def test_bullish_signal_without_position_recommends_buy() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="ALCISTA",
        confidence="0.80",
        expected_return="5.00",
    )

    decision = engine.evaluate(context)

    assert (
        decision.recommendation_type
        is RecommendationType.SIMULATED_BUY
    )

    assert (
        decision.asset.action
        is RecommendationAssetAction.ADD
    )


def test_bullish_signal_with_position_recommends_hold() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="ALCISTA",
        confidence="0.80",
        expected_return="5.00",
        with_position=True,
    )

    decision = engine.evaluate(context)

    assert (
        decision.recommendation_type
        is RecommendationType.HOLD
    )

    assert (
        decision.asset.action
        is RecommendationAssetAction.HOLD
    )


def test_bearish_signal_without_position_recommends_avoid() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="BAJISTA",
        confidence="0.70",
        expected_return="-5.00",
    )

    decision = engine.evaluate(context)

    assert (
        decision.recommendation_type
        is RecommendationType.AVOID
    )

    assert (
        decision.asset.action
        is RecommendationAssetAction.AVOID
    )


def test_bearish_signal_with_position_recommends_reduce() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="BAJISTA",
        confidence="0.70",
        expected_return="-5.00",
        with_position=True,
    )

    decision = engine.evaluate(context)

    assert (
        decision.recommendation_type
        is RecommendationType.REDUCE
    )

    assert (
        decision.asset.action
        is RecommendationAssetAction.REDUCE
    )


def test_neutral_signal_recommends_watch() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="NEUTRAL",
        confidence="0.80",
        expected_return="0",
    )

    decision = engine.evaluate(context)

    assert (
        decision.recommendation_type
        is RecommendationType.WATCH
    )

    assert (
        decision.asset.action
        is RecommendationAssetAction.WATCH
    )


def test_low_confidence_bullish_signal_recommends_watch() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="ALCISTA",
        confidence="0.50",
        expected_return="5.00",
    )

    decision = engine.evaluate(context)

    assert (
        decision.recommendation_type
        is RecommendationType.WATCH
    )


def test_conservative_profile_blocks_simulated_buy() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="ALCISTA",
        confidence="0.90",
        expected_return="8.00",
        classification="CONSERVADOR",
    )

    decision = engine.evaluate(context)

    assert (
        decision.recommendation_type
        is RecommendationType.WATCH
    )

    assert (
        decision.asset.action
        is RecommendationAssetAction.WATCH
    )

    assert (
        decision.risk_level
        is RecommendationRiskLevel.VERY_LOW
    )


def test_aggressive_profile_maps_to_very_high_risk() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="NEUTRAL",
        confidence="0.60",
        expected_return="0",
        classification="AGRESIVO",
    )

    decision = engine.evaluate(context)

    assert (
        decision.risk_level
        is RecommendationRiskLevel.VERY_HIGH
    )


def test_decision_contains_explainable_evidence() -> None:
    engine = RecommendationEngine()

    context = build_context(
        trend="ALCISTA",
        confidence="0.80",
        expected_return="5.00",
    )

    decision = engine.evaluate(context)

    assert len(decision.evidences) == 2

    assert (
        decision.evidences[0].source_entity
        == "ai.predicciones_activo"
    )

    assert (
        decision.evidences[1].source_entity
        == "profile.perfiles_riesgo"
    )