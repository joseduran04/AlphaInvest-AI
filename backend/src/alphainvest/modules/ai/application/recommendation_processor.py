from decimal import Decimal
from uuid import UUID

from alphainvest.modules.ai.application.recommendation_context_builder import (
    RecommendationContextBuilder,
)
from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisRequestStatus,
    AnalysisType,
)
from alphainvest.modules.ai.domain.recommendation_engine import (
    RecommendationEngine,
)
from alphainvest.modules.ai.domain.recommendation_enums import (
    AnalysisEvidenceType,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)


class RecommendationProcessor:
    """Procesa una solicitud RECOMENDACION pendiente."""

    def __init__(
        self,
        *,
        ai_repository: AIRepository,
        context_builder: RecommendationContextBuilder,
        engine: RecommendationEngine,
    ) -> None:
        self._ai_repository = ai_repository
        self._context_builder = context_builder
        self._engine = engine

    async def process(
        self,
        *,
        request_id: UUID,
    ) -> None:
        request = (
            await self._ai_repository
            .get_analysis_request(
                request_id
            )
        )

        if request is None:
            raise ValueError(
                "La solicitud de recomendación "
                "no existe"
            )

        if (
            request.tipo_analisis
            != AnalysisType.RECOMMENDATION.value
        ):
            raise ValueError(
                "La solicitud no corresponde "
                "a RECOMENDACION"
            )

        if (
            request.estado
            != AnalysisRequestStatus.PENDING.value
        ):
            raise ValueError(
                "La solicitud RECOMENDACION "
                "no se encuentra PENDIENTE"
            )

        existing = (
            await self._ai_repository
            .get_recommendation_by_request(
                request_id=request.id
            )
        )

        if existing is not None:
            raise ValueError(
                "La solicitud ya tiene una "
                "recomendación persistida"
            )

        await (
            self._ai_repository
            .increment_analysis_request_attempt(
                request
            )
        )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .RUNNING
                    .value
                ),
                progress=Decimal("10"),
                error_message=None,
            )
        )

        await self._ai_repository.commit()

        context = await self._context_builder.build(
            request=request
        )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .RUNNING
                    .value
                ),
                progress=Decimal("40"),
                error_message=None,
            )
        )

        decision = self._engine.evaluate(
            context
        )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .RUNNING
                    .value
                ),
                progress=Decimal("60"),
                error_message=None,
            )
        )

        risk_profile_id = None

        if context.risk_profile is not None:
            risk_profile_id = (
                context.risk_profile.profile_id
            )

        portfolio_id = None

        if context.portfolio is not None:
            portfolio_id = (
                context.portfolio.portfolio_id
            )

        recommendation_parameters: dict[
            str,
            object,
        ] = {
            "asset_id": str(
                context.asset_id
            ),
        }

        request_parameters = request.parametros

        if isinstance(
            request_parameters,
            dict,
        ):
            prediction_request_id = (
                request_parameters.get(
                    "prediction_request_id"
                )
            )

            if isinstance(
                prediction_request_id,
                str,
            ):
                recommendation_parameters[
                    "prediction_request_id"
                ] = prediction_request_id

        if decision.parameters is not None:
            recommendation_parameters.update(
                decision.parameters
            )

        recommendation = (
            await self._ai_repository
            .create_recommendation(
                request_id=request.id,
                user_id=request.usuario_id,
                risk_profile_id=(
                    risk_profile_id
                ),
                portfolio_id=portfolio_id,
                model_version_id=(
                    context.model_version_id
                ),
                recommendation_type=(
                    decision
                    .recommendation_type
                    .value
                ),
                title=decision.title,
                summary=decision.summary,
                justification=(
                    decision.justification
                ),
                risk_level=(
                    decision.risk_level.value
                ),
                horizon=context.horizon,
                confidence=(
                    decision.confidence
                ),
                priority=decision.priority,
                warning=decision.warning,
                parameters=(
                    recommendation_parameters
                ),
                expiration_date=None,
            )
        )

        await (
            self._ai_repository
            .create_recommendation_asset(
                recommendation_id=(
                    recommendation.id
                ),
                asset_id=context.asset_id,
                action=(
                    decision.asset.action.value
                ),
                target_percentage=(
                    decision
                    .asset
                    .target_percentage
                ),
                reference_price=(
                    decision
                    .asset
                    .reference_price
                ),
                target_price=(
                    decision
                    .asset
                    .target_price
                ),
                loss_limit=(
                    decision
                    .asset
                    .loss_limit
                ),
                confidence=(
                    decision
                    .asset
                    .confidence
                ),
                priority=(
                    decision.asset.priority
                ),
                justification=(
                    decision
                    .asset
                    .justification
                ),
            )
        )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .RUNNING
                    .value
                ),
                progress=Decimal("80"),
                error_message=None,
            )
        )

        for evidence in decision.evidences:
            prediction_id = None

            if (
                evidence.evidence_type
                is AnalysisEvidenceType.MODEL
            ):
                prediction_id = (
                    context
                    .prediction
                    .prediction_id
                )

            await (
                self._ai_repository
                .create_analysis_evidence(
                    request_id=request.id,
                    recommendation_id=(
                        recommendation.id
                    ),
                    prediction_id=prediction_id,
                    evidence_type=(
                        evidence
                        .evidence_type
                        .value
                    ),
                    source_entity=(
                        evidence.source_entity
                    ),
                    source_identifier=(
                        evidence
                        .source_identifier
                    ),
                    description=(
                        evidence.description
                    ),
                    numeric_value=(
                        evidence.numeric_value
                    ),
                    unit=evidence.unit,
                    weight=evidence.weight,
                    contribution=(
                        evidence
                        .contribution
                        .value
                    ),
                    data=evidence.data,
                    evidence_date=None,
                )
            )

        await (
            self._ai_repository
            .update_analysis_request_status(
                request,
                status=(
                    AnalysisRequestStatus
                    .COMPLETED
                    .value
                ),
                progress=Decimal("100"),
                error_message=None,
            )
        )

        await self._ai_repository.commit()