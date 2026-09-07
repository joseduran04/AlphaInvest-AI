from alphainvest.modules.ai.domain.recommendation_enums import (
    AnalysisEvidenceType,
    EvidenceContribution,
    RecommendationAssetAction,
    RecommendationRiskLevel,
    RecommendationStatus,
    RecommendationType,
)


def test_recommendation_type_values() -> None:
    assert RecommendationType.WATCH.value == "OBSERVAR"
    assert (
        RecommendationType.SIMULATED_BUY.value
        == "COMPRAR_SIMULADO"
    )
    assert RecommendationType.HOLD.value == "MANTENER"
    assert RecommendationType.REDUCE.value == "REDUCIR"
    assert (
        RecommendationType.SIMULATED_SELL.value
        == "VENDER_SIMULADO"
    )
    assert RecommendationType.DIVERSIFY.value == "DIVERSIFICAR"
    assert RecommendationType.REBALANCE.value == "REBALANCEAR"
    assert RecommendationType.AVOID.value == "EVITAR"


def test_recommendation_risk_level_values() -> None:
    assert RecommendationRiskLevel.VERY_LOW.value == "MUY_BAJO"
    assert RecommendationRiskLevel.LOW.value == "BAJO"
    assert RecommendationRiskLevel.MEDIUM.value == "MEDIO"
    assert RecommendationRiskLevel.HIGH.value == "ALTO"
    assert RecommendationRiskLevel.VERY_HIGH.value == "MUY_ALTO"


def test_recommendation_status_values() -> None:
    assert RecommendationStatus.GENERATED.value == "GENERADA"
    assert RecommendationStatus.SHOWN.value == "MOSTRADA"
    assert RecommendationStatus.ACCEPTED.value == "ACEPTADA"
    assert RecommendationStatus.REJECTED.value == "RECHAZADA"
    assert RecommendationStatus.EXPIRED.value == "EXPIRADA"
    assert RecommendationStatus.WITHDRAWN.value == "RETIRADA"


def test_recommendation_asset_action_values() -> None:
    assert RecommendationAssetAction.WATCH.value == "OBSERVAR"
    assert RecommendationAssetAction.ADD.value == "AGREGAR"
    assert RecommendationAssetAction.HOLD.value == "MANTENER"
    assert RecommendationAssetAction.INCREASE.value == "AUMENTAR"
    assert RecommendationAssetAction.REDUCE.value == "REDUCIR"
    assert RecommendationAssetAction.REMOVE.value == "RETIRAR"
    assert RecommendationAssetAction.AVOID.value == "EVITAR"


def test_analysis_evidence_type_values() -> None:
    assert AnalysisEvidenceType.PRICE.value == "PRECIO"
    assert AnalysisEvidenceType.INDICATOR.value == "INDICADOR"
    assert AnalysisEvidenceType.SENTIMENT.value == "SENTIMIENTO"
    assert AnalysisEvidenceType.FUNDAMENTAL.value == "FUNDAMENTAL"
    assert AnalysisEvidenceType.RISK_PROFILE.value == "PERFIL_RIESGO"
    assert AnalysisEvidenceType.SIMULATION.value == "SIMULACION"
    assert AnalysisEvidenceType.PORTFOLIO.value == "PORTAFOLIO"
    assert AnalysisEvidenceType.MODEL.value == "MODELO"
    assert AnalysisEvidenceType.OTHER.value == "OTRA"


def test_evidence_contribution_values() -> None:
    assert EvidenceContribution.POSITIVE.value == "POSITIVA"
    assert EvidenceContribution.NEUTRAL.value == "NEUTRAL"
    assert EvidenceContribution.NEGATIVE.value == "NEGATIVA"