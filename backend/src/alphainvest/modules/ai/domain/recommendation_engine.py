from decimal import Decimal

from alphainvest.modules.ai.domain.recommendation_context import (
    RecommendationContext,
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

HIGH_CONFIDENCE = Decimal("0.70")
MEDIUM_CONFIDENCE = Decimal("0.55")

POSITIVE_RETURN_THRESHOLD = Decimal("1.00")
NEGATIVE_RETURN_THRESHOLD = Decimal("-1.00")


class RecommendationEngine:
    """Motor determinístico y explicable de recomendaciones."""

    def evaluate(
        self,
        context: RecommendationContext,
    ) -> RecommendationDecision:
        prediction = context.prediction

        evidences = [
            self._build_prediction_evidence(
                context,
            )
        ]

        risk_level = self._resolve_risk_level(
            context
        )

        risk_evidence = self._build_risk_evidence(
            context,
            risk_level,
        )

        if risk_evidence is not None:
            evidences.append(risk_evidence)

        has_open_position = (
            context.portfolio is not None
            and context.portfolio.position is not None
            and context.portfolio.position.status
            == "ABIERTA"
            and context.portfolio.position.quantity
            > Decimal("0")
        )

        strong_signal = (
            prediction.confidence >= HIGH_CONFIDENCE
        )

        medium_signal = (
            prediction.confidence >= MEDIUM_CONFIDENCE
        )

        expected_return = (
            prediction.expected_return_percentage
        )

        positive_return = (
            expected_return is not None
            and expected_return
            >= POSITIVE_RETURN_THRESHOLD
        )

        negative_return = (
            expected_return is not None
            and expected_return
            <= NEGATIVE_RETURN_THRESHOLD
        )

        if (
            prediction.trend == "ALCISTA"
            and strong_signal
            and positive_return
        ):
            return self._build_bullish_decision(
                context=context,
                has_open_position=has_open_position,
                risk_level=risk_level,
                evidences=tuple(evidences),
            )

        if (
            prediction.trend == "BAJISTA"
            and medium_signal
            and negative_return
        ):
            return self._build_bearish_decision(
                context=context,
                has_open_position=has_open_position,
                risk_level=risk_level,
                evidences=tuple(evidences),
            )

        return self._build_watch_decision(
            context=context,
            has_open_position=has_open_position,
            risk_level=risk_level,
            evidences=tuple(evidences),
        )

    def _build_bullish_decision(
        self,
        *,
        context: RecommendationContext,
        has_open_position: bool,
        risk_level: RecommendationRiskLevel,
        evidences: tuple[
            RecommendationEvidenceDecision,
            ...,
        ],
    ) -> RecommendationDecision:
        conservative_profile = (
            context.risk_profile is not None
            and context.risk_profile.classification
            in {
                "CONSERVADOR",
                "MODERADO_CONSERVADOR",
            }
        )

        if conservative_profile:
            return self._build_watch_decision(
                context=context,
                has_open_position=has_open_position,
                risk_level=risk_level,
                evidences=evidences,
            )

        if has_open_position:
            recommendation_type = (
                RecommendationType.HOLD
            )
            action = (
                RecommendationAssetAction.HOLD
            )
            title = "Mantener posición"
            summary = (
                "La señal de tendencia es favorable "
                "para una posición existente."
            )
        else:
            recommendation_type = (
                RecommendationType.SIMULATED_BUY
            )
            action = (
                RecommendationAssetAction.ADD
            )
            title = "Compra simulada"
            summary = (
                "La señal de tendencia es favorable "
                "y no existe una posición abierta."
            )

        return RecommendationDecision(
            recommendation_type=(
                recommendation_type
            ),
            title=title,
            summary=summary,
            justification=(
                "La predicción presenta tendencia "
                "ALCISTA, confianza alta y un "
                "rendimiento esperado positivo."
            ),
            risk_level=risk_level,
            confidence=context.prediction.confidence,
            priority=1,
            warning=(
                "Información educativa; no constituye "
                "asesoría financiera ni una instrucción "
                "de inversión real."
            ),
            asset=RecommendationAssetDecision(
                action=action,
                target_percentage=None,
                reference_price=(
                    context.latest_price
                    or context.prediction.base_price
                ),
                target_price=(
                    context.prediction.predicted_price
                ),
                loss_limit=None,
                confidence=(
                    context.prediction.confidence
                ),
                priority=1,
                justification=(
                    "La acción se deriva de una señal "
                    "alcista con confianza suficiente."
                ),
            ),
            evidences=evidences,
            parameters={
                "engine": "deterministic_v1",
                "high_confidence_threshold": (
                    str(HIGH_CONFIDENCE)
                ),
                "positive_return_threshold": (
                    str(POSITIVE_RETURN_THRESHOLD)
                ),
            },
        )

    def _build_bearish_decision(
        self,
        *,
        context: RecommendationContext,
        has_open_position: bool,
        risk_level: RecommendationRiskLevel,
        evidences: tuple[
            RecommendationEvidenceDecision,
            ...,
        ],
    ) -> RecommendationDecision:
        if has_open_position:
            recommendation_type = (
                RecommendationType.REDUCE
            )
            action = (
                RecommendationAssetAction.REDUCE
            )
            title = "Reducir exposición"
            summary = (
                "La predicción desfavorable sugiere "
                "reducir exposición simulada."
            )
        else:
            recommendation_type = (
                RecommendationType.AVOID
            )
            action = (
                RecommendationAssetAction.AVOID
            )
            title = "Evitar activo"
            summary = (
                "La señal actual no favorece agregar "
                "el activo al portafolio."
            )

        return RecommendationDecision(
            recommendation_type=(
                recommendation_type
            ),
            title=title,
            summary=summary,
            justification=(
                "La predicción presenta tendencia "
                "BAJISTA, confianza suficiente y un "
                "rendimiento esperado negativo."
            ),
            risk_level=risk_level,
            confidence=context.prediction.confidence,
            priority=1,
            warning=(
                "Información educativa; no constituye "
                "asesoría financiera ni una instrucción "
                "de inversión real."
            ),
            asset=RecommendationAssetDecision(
                action=action,
                target_percentage=None,
                reference_price=(
                    context.latest_price
                    or context.prediction.base_price
                ),
                target_price=(
                    context.prediction.predicted_price
                ),
                loss_limit=None,
                confidence=(
                    context.prediction.confidence
                ),
                priority=1,
                justification=(
                    "La acción se deriva de una señal "
                    "bajista con confianza suficiente."
                ),
            ),
            evidences=evidences,
            parameters={
                "engine": "deterministic_v1",
                "medium_confidence_threshold": (
                    str(MEDIUM_CONFIDENCE)
                ),
                "negative_return_threshold": (
                    str(NEGATIVE_RETURN_THRESHOLD)
                ),
            },
        )

    def _build_watch_decision(
        self,
        *,
        context: RecommendationContext,
        has_open_position: bool,
        risk_level: RecommendationRiskLevel,
        evidences: tuple[
            RecommendationEvidenceDecision,
            ...,
        ],
    ) -> RecommendationDecision:
        if has_open_position:
            recommendation_type = (
                RecommendationType.HOLD
            )
            action = (
                RecommendationAssetAction.HOLD
            )
            title = "Mantener y observar"
            summary = (
                "Las señales disponibles no justifican "
                "un cambio de exposición."
            )
        else:
            recommendation_type = (
                RecommendationType.WATCH
            )
            action = (
                RecommendationAssetAction.WATCH
            )
            title = "Observar activo"
            summary = (
                "Las señales disponibles todavía no "
                "son suficientemente concluyentes."
            )

        return RecommendationDecision(
            recommendation_type=(
                recommendation_type
            ),
            title=title,
            summary=summary,
            justification=(
                "La tendencia, confianza o rendimiento "
                "esperado no cumplen simultáneamente "
                "los criterios de una señal fuerte."
            ),
            risk_level=risk_level,
            confidence=context.prediction.confidence,
            priority=2,
            warning=(
                "Información educativa; no constituye "
                "asesoría financiera ni una instrucción "
                "de inversión real."
            ),
            asset=RecommendationAssetDecision(
                action=action,
                target_percentage=None,
                reference_price=(
                    context.latest_price
                    or context.prediction.base_price
                ),
                target_price=(
                    context.prediction.predicted_price
                ),
                loss_limit=None,
                confidence=(
                    context.prediction.confidence
                ),
                priority=2,
                justification=(
                    "Se mantiene una postura conservadora "
                    "ante evidencia insuficiente."
                ),
            ),
            evidences=evidences,
            parameters={
                "engine": "deterministic_v1",
            },
        )

    def _resolve_risk_level(
        self,
        context: RecommendationContext,
    ) -> RecommendationRiskLevel:
        profile = context.risk_profile

        if profile is None:
            return RecommendationRiskLevel.MEDIUM

        mapping = {
            "CONSERVADOR": (
                RecommendationRiskLevel.VERY_LOW
            ),
            "MODERADO_CONSERVADOR": (
                RecommendationRiskLevel.LOW
            ),
            "MODERADO": (
                RecommendationRiskLevel.MEDIUM
            ),
            "MODERADO_AGRESIVO": (
                RecommendationRiskLevel.HIGH
            ),
            "AGRESIVO": (
                RecommendationRiskLevel.VERY_HIGH
            ),
        }

        return mapping.get(
            profile.classification,
            RecommendationRiskLevel.MEDIUM,
        )

    def _build_prediction_evidence(
        self,
        context: RecommendationContext,
    ) -> RecommendationEvidenceDecision:
        prediction = context.prediction

        contribution = EvidenceContribution.NEUTRAL

        if prediction.trend == "ALCISTA":
            contribution = EvidenceContribution.POSITIVE
        elif prediction.trend == "BAJISTA":
            contribution = EvidenceContribution.NEGATIVE

        return RecommendationEvidenceDecision(
            evidence_type=AnalysisEvidenceType.MODEL,
            source_entity="ai.predicciones_activo",
            source_identifier=str(
                prediction.prediction_id
            ),
            description=(
                "Predicción de tendencia utilizada "
                "por el motor de recomendación."
            ),
            numeric_value=prediction.confidence,
            unit="PROBABILIDAD",
            weight=prediction.confidence,
            contribution=contribution,
            data={
                "trend": prediction.trend,
                "expected_return_percentage": (
                    str(
                        prediction
                        .expected_return_percentage
                    )
                    if prediction
                    .expected_return_percentage
                    is not None
                    else None
                ),
                "predicted_price": str(
                    prediction.predicted_price
                ),
            },
        )

    def _build_risk_evidence(
        self,
        context: RecommendationContext,
        risk_level: RecommendationRiskLevel,
    ) -> RecommendationEvidenceDecision | None:
        profile = context.risk_profile

        if profile is None:
            return None

        return RecommendationEvidenceDecision(
            evidence_type=(
                AnalysisEvidenceType.RISK_PROFILE
            ),
            source_entity="profile.perfiles_riesgo",
            source_identifier=str(
                profile.profile_id
            ),
            description=(
                "Perfil de riesgo vigente utilizado "
                "para contextualizar la recomendación."
            ),
            numeric_value=profile.score,
            unit="PUNTUACION",
            weight=profile.confidence,
            contribution=EvidenceContribution.NEUTRAL,
            data={
                "classification": (
                    profile.classification
                ),
                "recommendation_risk_level": (
                    risk_level.value
                ),
            },
        )