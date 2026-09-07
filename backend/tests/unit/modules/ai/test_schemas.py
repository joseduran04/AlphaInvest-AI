from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisHorizon,
)
from alphainvest.modules.ai.domain.enums import (
    AIModelStatus,
)
from alphainvest.modules.ai.presentation.schemas import (
    AIModelResponse,
    AssetAnalysisRequestCreate,
    ModelVersionResponse,
)

pytestmark = pytest.mark.unit


def test_ai_model_response_from_attributes() -> None:
    now = datetime.now(UTC)

    model = SimpleNamespace(
        id=uuid4(),
        codigo="PREDICCION_TENDENCIA",
        nombre="Predicción de tendencia",
        tipo="CLASIFICACION",
        objetivo="Clasificar tendencia",
        descripcion="Modelo de prueba",
        estado="ACTIVO",
        fecha_creacion=now,
        fecha_actualizacion=now,
    )

    response = AIModelResponse.model_validate(model)

    assert response.id == model.id
    assert response.code == model.codigo
    assert response.name == model.nombre
    assert response.type == model.tipo
    assert response.status == AIModelStatus.ACTIVE


def test_model_version_response_from_attributes() -> None:
    now = datetime.now(UTC)
    model_id = uuid4()

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=model_id,
        version="1.0.0",
        ruta_artefacto="models/trend/1.0.0",
        checksum="abc123",
        algoritmo="XGBoost",
        framework="xgboost",
        hiperparametros={"depth": 5},
        metricas={"accuracy": 0.85},
        conjunto_entrenamiento={"rows": 1000},
        fecha_entrenamiento=now,
        fecha_activacion=now,
        fecha_desactivacion=None,
        activa=True,
        creada_por=None,
        fecha_registro=now,
    )

    response = ModelVersionResponse.model_validate(
        version
    )

    assert response.model_id == model_id
    assert response.version == "1.0.0"
    assert response.active is True
    assert response.hyperparameters == {
        "depth": 5
    }


def test_asset_analysis_request_create() -> None:
    asset_id = uuid4()

    request = AssetAnalysisRequestCreate(
        asset_id=asset_id,
        horizon=AnalysisHorizon.SHORT_TERM,
        reference_date=date(2026, 8, 14),
    )

    assert request.asset_id == asset_id

    assert (
        request.horizon
        == AnalysisHorizon.SHORT_TERM
    )

    assert (
        request.reference_date
        == date(2026, 8, 14)
    )


def test_asset_analysis_defaults_to_short_term() -> None:
    request = AssetAnalysisRequestCreate(
        asset_id=uuid4(),
        reference_date=date(2026, 8, 14),
    )

    assert (
        request.horizon
        == AnalysisHorizon.SHORT_TERM
    )