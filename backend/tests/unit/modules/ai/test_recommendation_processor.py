from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.recommendation_processor import (
    RecommendationProcessor,
)
from alphainvest.modules.ai.domain.recommendation_context import (
    RecommendationContext,
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

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_processes_pending_recommendation_request(
) -> None:
    request_id = uuid4()
    user_id = uuid4()
    asset_id = uuid4()
    prediction_id = uuid4()
    prediction_request_id = uuid4()
    version_id = uuid4()
    profile_id = uuid4()
    recommendation_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        usuario_id=user_id,
        tipo_analisis="RECOMENDACION",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
        parametros={
            "asset_id": str(asset_id),
            "prediction_request_id": str(
                prediction_request_id
            ),
        },
    )

    context = RecommendationContext(
        request_id=request_id,
        user_id=user_id,
        asset_id=asset_id,
        model_version_id=version_id,
        horizon="CORTO_PLAZO",
        prediction=(
            RecommendationPredictionSignal(
                prediction_id=prediction_id,
                asset_id=asset_id,
                base_date=date(
                    2026,
                    8,
                    27,
                ),
                target_date=date(
                    2026,
                    8,
                    28,
                ),
                horizon="CORTO_PLAZO",
                base_price=Decimal("100"),
                predicted_price=(
                    Decimal("105")
                ),
                expected_return_percentage=(
                    Decimal("5")
                ),
                trend="ALCISTA",
                confidence=Decimal("0.80"),
                bullish_probability=None,
                neutral_probability=None,
                bearish_probability=None,
            )
        ),
        latest_price=Decimal("101"),
        indicators=(),
        risk_profile=(
            RecommendationRiskProfileSignal(
                profile_id=profile_id,
                classification="MODERADO",
                score=Decimal("50"),
                confidence=Decimal("0.90"),
            )
        ),
        portfolio=None,
    )

    decision = RecommendationDecision(
        recommendation_type=(
            RecommendationType.SIMULATED_BUY
        ),
        title="Compra simulada",
        summary="Señal favorable",
        justification=(
            "Tendencia alcista"
        ),
        risk_level=(
            RecommendationRiskLevel.MEDIUM
        ),
        confidence=Decimal("0.80"),
        priority=1,
        warning="Información educativa",
        asset=RecommendationAssetDecision(
            action=(
                RecommendationAssetAction.ADD
            ),
            target_percentage=None,
            reference_price=Decimal("101"),
            target_price=Decimal("105"),
            loss_limit=None,
            confidence=Decimal("0.80"),
            priority=1,
            justification=(
                "Señal alcista"
            ),
        ),
        evidences=(
            RecommendationEvidenceDecision(
                evidence_type=(
                    AnalysisEvidenceType.MODEL
                ),
                source_entity=(
                    "ai.predicciones_activo"
                ),
                source_identifier=str(
                    prediction_id
                ),
                description=(
                    "Predicción utilizada"
                ),
                numeric_value=(
                    Decimal("0.80")
                ),
                unit="PROBABILIDAD",
                weight=Decimal("0.80"),
                contribution=(
                    EvidenceContribution.POSITIVE
                ),
                data={
                    "trend": "ALCISTA",
                },
            ),
            RecommendationEvidenceDecision(
                evidence_type=(
                    AnalysisEvidenceType
                    .RISK_PROFILE
                ),
                source_entity=(
                    "profile.perfiles_riesgo"
                ),
                source_identifier=str(
                    profile_id
                ),
                description=(
                    "Perfil utilizado"
                ),
                numeric_value=Decimal("50"),
                unit="PUNTUACION",
                weight=Decimal("0.90"),
                contribution=(
                    EvidenceContribution.NEUTRAL
                ),
                data={
                    "classification": (
                        "MODERADO"
                    ),
                },
            ),
        ),
        parameters={
            "engine": "deterministic_v1",
        },
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        get_recommendation_by_request=AsyncMock(
            return_value=None
        ),
        increment_analysis_request_attempt=(
            AsyncMock()
        ),
        update_analysis_request_status=(
            AsyncMock()
        ),
        create_recommendation=AsyncMock(
            return_value=SimpleNamespace(
                id=recommendation_id
            )
        ),
        create_recommendation_asset=(
            AsyncMock()
        ),
        create_analysis_evidence=AsyncMock(),
        commit=AsyncMock(),
    )

    context_builder = SimpleNamespace(
        build=AsyncMock(
            return_value=context
        )
    )

    engine = SimpleNamespace(
        evaluate=Mock(
            return_value=decision
        )
    )

    processor = RecommendationProcessor(
        ai_repository=repository,
        context_builder=context_builder,
        engine=engine,
    )

    await processor.process(
        request_id=request_id
    )

    (
        repository
        .increment_analysis_request_attempt
        .assert_awaited_once_with(
            request
        )
    )

    context_builder.build.assert_awaited_once_with(
        request=request
    )

    engine.evaluate.assert_called_once_with(
        context
    )

    (
        repository
        .create_recommendation
        .assert_awaited_once()
    )

    recommendation_call = (
        repository
        .create_recommendation
        .await_args
    )

    assert recommendation_call is not None

    assert (
        recommendation_call
        .kwargs["model_version_id"]
        == version_id
    )

    assert (
        recommendation_call
        .kwargs["risk_profile_id"]
        == profile_id
    )

    assert (
        recommendation_call
        .kwargs["parameters"]["engine"]
        == "deterministic_v1"
    )

    assert (
        recommendation_call
        .kwargs["parameters"][
            "prediction_request_id"
        ]
        == str(prediction_request_id)
    )

    (
        repository
        .create_recommendation_asset
        .assert_awaited_once()
    )

    assert (
        repository
        .create_analysis_evidence
        .await_count
        == 2
    )

    evidence_calls = (
        repository
        .create_analysis_evidence
        .await_args_list
    )

    assert (
        evidence_calls[0]
        .kwargs["prediction_id"]
        == prediction_id
    )

    assert (
        evidence_calls[1]
        .kwargs["prediction_id"]
        is None
    )

    assert (
        repository
        .update_analysis_request_status
        .await_count
        == 5
    )

    status_calls = (
        repository
        .update_analysis_request_status
        .await_args_list
    )

    final_status_call = status_calls[-1]

    assert (
        final_status_call.kwargs["status"]
        == "COMPLETADA"
    )

    assert (
        final_status_call.kwargs["progress"]
        == Decimal("100")
    )

    assert (
        final_status_call.kwargs["error_message"]
        is None
    )

    assert repository.commit.await_count == 2


@pytest.mark.asyncio
async def test_rejects_non_recommendation_request(
) -> None:
    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="ACTIVO",
        estado="PENDIENTE",
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        )
    )

    processor = RecommendationProcessor(
        ai_repository=repository,
        context_builder=SimpleNamespace(),
        engine=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="RECOMENDACION",
    ):
        await processor.process(
            request_id=request.id
        )


@pytest.mark.asyncio
async def test_rejects_non_pending_recommendation(
) -> None:
    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="RECOMENDACION",
        estado="EJECUTANDO",
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        )
    )

    processor = RecommendationProcessor(
        ai_repository=repository,
        context_builder=SimpleNamespace(),
        engine=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="PENDIENTE",
    ):
        await processor.process(
            request_id=request.id
        )


@pytest.mark.asyncio
async def test_rejects_duplicate_recommendation(
) -> None:
    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="RECOMENDACION",
        estado="PENDIENTE",
    )

    repository = SimpleNamespace(
        get_analysis_request=AsyncMock(
            return_value=request
        ),
        get_recommendation_by_request=AsyncMock(
            return_value=SimpleNamespace(
                id=uuid4()
            )
        ),
    )

    processor = RecommendationProcessor(
        ai_repository=repository,
        context_builder=SimpleNamespace(),
        engine=SimpleNamespace(),
    )

    with pytest.raises(
        ValueError,
        match="ya tiene",
    ):
        await processor.process(
            request_id=request.id
        )