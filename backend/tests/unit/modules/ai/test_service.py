from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from alphainvest.modules.ai.application.service import (
    AIService,
)
from alphainvest.modules.ai.domain.enums import (
    AIModelStatus,
)
from alphainvest.modules.ai.domain.exceptions import (
    ActiveModelVersionNotFoundError,
    AIModelNotActiveError,
    AIModelNotFoundError,
    ModelVersionAlreadyExistsError,
)
from alphainvest.modules.ai.presentation.schemas import (
    AIModelStatusUpdateRequest,
    ModelVersionCreateRequest,
)

pytestmark = pytest.mark.unit


def build_model(
    *,
    status: str = "ACTIVO",
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=uuid4(),
        codigo="PREDICCION_TENDENCIA",
        nombre="Predicción de tendencia",
        tipo="CLASIFICACION",
        objetivo="Clasificar tendencia",
        descripcion="Modelo de prueba",
        estado=status,
        fecha_creacion=now,
        fecha_actualizacion=now,
    )


def build_version(
    model_id: object,
) -> SimpleNamespace:
    now = datetime.now(UTC)

    return SimpleNamespace(
        id=uuid4(),
        modelo_id=model_id,
        version="1.0.0",
        ruta_artefacto="models/trend/1.0.0",
        checksum="checksum",
        algoritmo="XGBoost",
        framework="xgboost",
        hiperparametros={},
        metricas={},
        conjunto_entrenamiento={},
        fecha_entrenamiento=now,
        fecha_activacion=now,
        fecha_desactivacion=None,
        activa=True,
        creada_por=None,
        fecha_registro=now,
    )


@pytest.mark.asyncio
async def test_list_models() -> None:
    repository = MagicMock()
    repository.list_models = AsyncMock()

    model = build_model()

    repository.list_models.return_value = (
        [model],
        1,
    )

    service = AIService(repository)

    response = await service.list_models(
        search=None,
        model_type=None,
        status=AIModelStatus.ACTIVE,
        limit=20,
        offset=0,
    )

    assert response.total == 1
    assert response.items[0].code == model.codigo

    repository.list_models.assert_awaited_once_with(
        search=None,
        model_type=None,
        status="ACTIVO",
        limit=20,
        offset=0,
    )


@pytest.mark.asyncio
async def test_get_model() -> None:
    repository = MagicMock()
    repository.get_model = AsyncMock()

    model = build_model()
    repository.get_model.return_value = model

    service = AIService(repository)

    response = await service.get_model(
        model_id=model.id
    )

    assert response.id == model.id
    assert response.code == model.codigo


@pytest.mark.asyncio
async def test_get_model_not_found() -> None:
    repository = MagicMock()
    repository.get_model = AsyncMock(
        return_value=None
    )

    service = AIService(repository)

    with pytest.raises(AIModelNotFoundError):
        await service.get_model(
            model_id=uuid4()
        )


@pytest.mark.asyncio
async def test_get_active_version() -> None:
    repository = MagicMock()
    repository.get_model = AsyncMock()
    repository.get_active_version_for_model = (
        AsyncMock()
    )

    model = build_model()
    version = build_version(model.id)

    repository.get_model.return_value = model
    repository.get_active_version_for_model.return_value = (
        version
    )

    service = AIService(repository)

    response = await service.get_active_version(
        model_id=model.id
    )

    assert response.model.id == model.id
    assert response.version.id == version.id
    assert response.version.active is True


@pytest.mark.asyncio
async def test_get_active_version_not_found() -> None:
    repository = MagicMock()
    repository.get_model = AsyncMock()
    repository.get_active_version_for_model = (
        AsyncMock(return_value=None)
    )

    model = build_model()
    repository.get_model.return_value = model

    service = AIService(repository)

    with pytest.raises(
        ActiveModelVersionNotFoundError
    ):
        await service.get_active_version(
            model_id=model.id
        )


@pytest.mark.asyncio
async def test_update_model_status() -> None:
    repository = MagicMock()
    repository.get_model = AsyncMock()
    repository.update_model_status = AsyncMock()
    repository.commit = AsyncMock()

    model = build_model(
        status="DESARROLLO"
    )
    updated = build_model(
        status="VALIDACION"
    )
    updated.id = model.id

    repository.get_model.return_value = model
    repository.update_model_status.return_value = (
        updated
    )

    service = AIService(repository)

    response = await service.update_model_status(
        model_id=model.id,
        request=AIModelStatusUpdateRequest(
            status=AIModelStatus.VALIDATION
        ),
    )

    assert response.status == AIModelStatus.VALIDATION

    repository.update_model_status.assert_awaited_once_with(
        model,
        status="VALIDACION",
    )
    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_model_version() -> None:
    repository = MagicMock()
    repository.get_model = AsyncMock()
    repository.create_model_version = AsyncMock()
    repository.commit = AsyncMock()

    model = build_model()
    version = build_version(model.id)
    version.activa = False
    version.fecha_activacion = None

    repository.get_model.return_value = model
    repository.create_model_version.return_value = (
        version
    )

    service = AIService(repository)

    response = await service.create_model_version(
        model_id=model.id,
        user_id=uuid4(),
        request=ModelVersionCreateRequest(
            version="1.0.0",
            artifact_path="models/trend/1.0.0",
            checksum="checksum",
            algorithm="XGBoost",
            framework="xgboost",
            hyperparameters={},
            metrics={},
            training_dataset={},
            trained_at=datetime.now(UTC),
        ),
    )

    assert response.version == "1.0.0"
    assert response.active is False


@pytest.mark.asyncio
async def test_create_model_version_conflict() -> None:
    repository = MagicMock()
    repository.get_model = AsyncMock()
    repository.create_model_version = AsyncMock(
        side_effect=IntegrityError(
            "statement",
            {},
            Exception("duplicate"),
        )
    )
    repository.rollback = AsyncMock()

    model = build_model()
    repository.get_model.return_value = model

    service = AIService(repository)

    with pytest.raises(
        ModelVersionAlreadyExistsError
    ):
        await service.create_model_version(
            model_id=model.id,
            user_id=uuid4(),
            request=ModelVersionCreateRequest(
                version="1.0.0",
                artifact_path="models/test",
                checksum="checksum",
                algorithm="XGBoost",
                framework="xgboost",
                trained_at=datetime.now(UTC),
            ),
        )

    repository.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_activate_model_version() -> None:
    repository = MagicMock()
    repository.get_model_version = AsyncMock()
    repository.get_model = AsyncMock()
    repository.activate_model_version = AsyncMock()
    repository.commit = AsyncMock()

    model = build_model(status="ACTIVO")
    version = build_version(model.id)

    version.activa = False
    version.fecha_activacion = None

    activated = build_version(model.id)
    activated.id = version.id
    activated.activa = True

    repository.get_model_version.return_value = (
        version
    )
    repository.get_model.return_value = model
    repository.activate_model_version.return_value = (
        activated
    )

    service = AIService(repository)

    response = await service.activate_model_version(
        version_id=version.id
    )

    assert response.id == version.id
    assert response.active is True

    repository.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_activate_model_version_requires_active_model(
) -> None:
    repository = MagicMock()
    repository.get_model_version = AsyncMock()
    repository.get_model = AsyncMock()

    model = build_model(status="DESARROLLO")
    version = build_version(model.id)

    version.activa = False
    version.fecha_activacion = None

    repository.get_model_version.return_value = (
        version
    )
    repository.get_model.return_value = model

    service = AIService(repository)

    with pytest.raises(AIModelNotActiveError):
        await service.activate_model_version(
            version_id=version.id
        )


@pytest.mark.asyncio
async def test_deactivate_model_version() -> None:
    repository = MagicMock()
    repository.get_model_version = AsyncMock()
    repository.deactivate_model_version = AsyncMock()
    repository.commit = AsyncMock()

    model_id = uuid4()

    version = build_version(model_id)

    deactivated = build_version(model_id)
    deactivated.id = version.id
    deactivated.activa = False
    deactivated.fecha_desactivacion = (
        datetime.now(UTC)
    )

    repository.get_model_version.return_value = (
        version
    )
    repository.deactivate_model_version.return_value = (
        deactivated
    )

    service = AIService(repository)

    response = (
        await service.deactivate_model_version(
            version_id=version.id
        )
    )

    assert response.active is False
    repository.commit.assert_awaited_once()