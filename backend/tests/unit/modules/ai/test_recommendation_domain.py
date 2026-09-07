from datetime import date
from decimal import Decimal
from uuid import uuid4

from alphainvest.modules.ai.domain.recommendation_context import (
    RecommendationContext,
    RecommendationIndicatorSignal,
    RecommendationPortfolioSignal,
    RecommendationPositionSignal,
    RecommendationPredictionSignal,
    RecommendationRiskProfileSignal,
)
from alphainvest.modules.ai.domain.recommendation_decision import (
    RecommendationAssetDecision,
    RecommendationDecision,
    RecommendationEvidenceDecision,
)
from alphainvest.modules.ai.domain.recommendation_enums import (
    AnalysisEvidenceType,
    EvidenceContribution,
    RecommendationAssetAction,
    RecommendationRiskLevel,
    RecommendationType,
)


def test_recommendation_context_with_full_data() -> None:
    request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    version_id = uuid4()

    prediction = RecommendationPredictionSignal(
        prediction_id=uuid4(),
        asset_id=asset_id,
        base_date=date(2026, 8, 27),
        target_date=date(2026, 8, 28),
        horizon="CORTO_PLAZO",
        base_price=Decimal("100"),
        predicted_price=Decimal("105"),
        expected_return_percentage=Decimal("5"),
        trend="ALCISTA",
        confidence=Decimal("0.80"),
        bullish_probability=Decimal("0.80"),
        neutral_probability=Decimal("0.10"),
        bearish_probability=Decimal("0.10"),
    )

    indicator = RecommendationIndicatorSignal(
        indicator_type="EMA",
        period="20D",
        value=Decimal("99"),
        date=date(2026, 8, 27),
    )

    profile = RecommendationRiskProfileSignal(
        profile_id=uuid4(),
        classification="MODERADO",
        score=Decimal("50"),
        confidence=Decimal("0.90"),
    )

    position = RecommendationPositionSignal(
        position_id=uuid4(),
        quantity=Decimal("10"),
        average_purchase_price=Decimal("95"),
        total_cost=Decimal("950"),
        current_price=Decimal("100"),
        current_value=Decimal("1000"),
        profit_loss=Decimal("50"),
        return_percentage=Decimal("5.26315789"),
        status="ABIERTA",
    )

    portfolio = RecommendationPortfolioSignal(
        portfolio_id=uuid4(),
        initial_capital=Decimal("10000"),
        cash_balance=Decimal("5000"),
        status="ACTIVO",
        position=position,
    )

    context = RecommendationContext(
        request_id=request_id,
        user_id=user_id,
        asset_id=asset_id,
        model_version_id=version_id,
        horizon="CORTO_PLAZO",
        prediction=prediction,
        latest_price=Decimal("100"),
        indicators=(indicator,),
        risk_profile=profile,
        portfolio=portfolio,
    )

    assert context.request_id == request_id
    assert context.asset_id == asset_id
    assert context.prediction.trend == "ALCISTA"
    assert context.risk_profile is not None
    assert context.risk_profile.classification == "MODERADO"
    assert context.portfolio is not None
    assert context.portfolio.position is not None
    assert (
        context.portfolio.position.quantity
        == Decimal("10")
    )


def test_recommendation_context_allows_optional_context() -> None:
    asset_id = uuid4()

    prediction = RecommendationPredictionSignal(
        prediction_id=uuid4(),
        asset_id=asset_id,
        base_date=date(2026, 8, 27),
        target_date=date(2026, 8, 28),
        horizon="CORTO_PLAZO",
        base_price=Decimal("100"),
        predicted_price=Decimal("100"),
        expected_return_percentage=Decimal("0"),
        trend="NEUTRAL",
        confidence=Decimal("0.50"),
        bullish_probability=None,
        neutral_probability=None,
        bearish_probability=None,
    )

    context = RecommendationContext(
        request_id=uuid4(),
        user_id=uuid4(),
        asset_id=asset_id,
        model_version_id=uuid4(),
        horizon="CORTO_PLAZO",
        prediction=prediction,
        latest_price=None,
        indicators=(),
        risk_profile=None,
        portfolio=None,
    )

    assert context.latest_price is None
    assert context.indicators == ()
    assert context.risk_profile is None
    assert context.portfolio is None


def test_recommendation_decision() -> None:
    evidence = RecommendationEvidenceDecision(
        evidence_type=AnalysisEvidenceType.MODEL,
        source_entity="ai.predicciones_activo",
        source_identifier=None,
        description="Tendencia alcista.",
        numeric_value=Decimal("0.80"),
        unit=None,
        weight=Decimal("0.60"),
        contribution=EvidenceContribution.POSITIVE,
        data={
            "trend": "ALCISTA",
        },
    )

    asset_decision = RecommendationAssetDecision(
        action=RecommendationAssetAction.WATCH,
        target_percentage=None,
        reference_price=Decimal("100"),
        target_price=Decimal("105"),
        loss_limit=None,
        confidence=Decimal("0.80"),
        priority=1,
        justification="Se recomienda observación.",
    )

    decision = RecommendationDecision(
        recommendation_type=RecommendationType.WATCH,
        title="Observar activo",
        summary="Se detecta una señal favorable.",
        justification=(
            "La predicción disponible muestra "
            "una tendencia favorable."
        ),
        risk_level=RecommendationRiskLevel.MEDIUM,
        confidence=Decimal("0.80"),
        priority=1,
        warning=(
            "Información educativa; no constituye "
            "asesoría financiera."
        ),
        asset=asset_decision,
        evidences=(evidence,),
        parameters={
            "engine": "deterministic_v1",
        },
    )

    assert (
        decision.recommendation_type
        is RecommendationType.WATCH
    )

    assert (
        decision.asset.action
        is RecommendationAssetAction.WATCH
    )

    assert len(decision.evidences) == 1

    assert (
        decision.evidences[0].contribution
        is EvidenceContribution.POSITIVE
    )