from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.modules.ai.infrastructure.models import (
    AnalysisEvidenceModel,
    RecommendationAssetModel,
    RecommendationModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)


def _build_session() -> AsyncMock:
    return AsyncMock(
        spec=AsyncSession,
    )


@pytest.mark.asyncio
async def test_create_recommendation() -> None:
    session = _build_session()
    repository = AIRepository(session)

    request_id = uuid4()
    user_id = uuid4()
    model_version_id = uuid4()

    recommendation = await repository.create_recommendation(
        request_id=request_id,
        user_id=user_id,
        risk_profile_id=None,
        portfolio_id=None,
        model_version_id=model_version_id,
        recommendation_type="OBSERVAR",
        title="Observar activo",
        summary="Resumen educativo.",
        justification="Justificación educativa.",
        risk_level="MEDIO",
        horizon="CORTO_PLAZO",
        confidence=Decimal("0.75"),
        priority=1,
        warning="No constituye asesoría financiera.",
        parameters={"source": "test"},
        expiration_date=None,
    )

    assert isinstance(
        recommendation,
        RecommendationModel,
    )

    assert recommendation.solicitud_id == request_id
    assert recommendation.usuario_id == user_id
    assert (
        recommendation.version_modelo_id
        == model_version_id
    )
    assert recommendation.tipo == "OBSERVAR"
    assert recommendation.estado == "GENERADA"

    session.add.assert_called_once_with(
        recommendation
    )
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        recommendation
    )


@pytest.mark.asyncio
async def test_create_recommendation_asset() -> None:
    session = _build_session()
    repository = AIRepository(session)

    recommendation_id = uuid4()
    asset_id = uuid4()

    recommendation_asset = (
        await repository.create_recommendation_asset(
            recommendation_id=recommendation_id,
            asset_id=asset_id,
            action="OBSERVAR",
            target_percentage=None,
            reference_price=Decimal("100"),
            target_price=Decimal("105"),
            loss_limit=None,
            confidence=Decimal("0.80"),
            priority=1,
            justification="Prueba.",
        )
    )

    assert isinstance(
        recommendation_asset,
        RecommendationAssetModel,
    )

    assert (
        recommendation_asset.recomendacion_id
        == recommendation_id
    )
    assert recommendation_asset.activo_id == asset_id
    assert recommendation_asset.accion == "OBSERVAR"

    session.add.assert_called_once_with(
        recommendation_asset
    )
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        recommendation_asset
    )


@pytest.mark.asyncio
async def test_create_analysis_evidence() -> None:
    session = _build_session()
    repository = AIRepository(session)

    request_id = uuid4()
    recommendation_id = uuid4()

    evidence_date = datetime.now(UTC)

    evidence = await repository.create_analysis_evidence(
        request_id=request_id,
        recommendation_id=recommendation_id,
        prediction_id=None,
        evidence_type="MODELO",
        source_entity="ai.predicciones_activo",
        source_identifier=None,
        description="Predicción utilizada.",
        numeric_value=Decimal("0.75"),
        unit=None,
        weight=Decimal("0.50"),
        contribution="POSITIVA",
        data={"test": True},
        evidence_date=evidence_date,
    )

    assert isinstance(
        evidence,
        AnalysisEvidenceModel,
    )

    assert evidence.solicitud_id == request_id
    assert (
        evidence.recomendacion_id
        == recommendation_id
    )
    assert evidence.tipo_evidencia == "MODELO"
    assert evidence.contribucion == "POSITIVA"

    session.add.assert_called_once_with(
        evidence
    )
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        evidence
    )


@pytest.mark.asyncio
async def test_get_recommendation_by_request() -> None:
    session = _build_session()
    repository = AIRepository(session)

    request_id = uuid4()

    expected = RecommendationModel()

    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = (
        expected
    )

    session.execute.return_value = scalar_result

    result = await repository.get_recommendation_by_request(
        request_id=request_id,
    )

    assert result is expected

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_analysis_evidence_for_recommendation() -> None:
    session = _build_session()
    repository = AIRepository(session)

    recommendation_id = uuid4()

    evidence = AnalysisEvidenceModel()

    scalars = MagicMock()
    scalars.all.return_value = [evidence]

    execute_result = MagicMock()
    execute_result.scalars.return_value = scalars

    session.execute.return_value = execute_result

    result = (
        await repository.list_analysis_evidence_for_recommendation(
            recommendation_id=recommendation_id,
        )
    )

    assert result == [evidence]

    session.execute.assert_awaited_once()