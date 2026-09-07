from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.trend_model_runtime_service import (
    TrendModelRuntimeService,
)
from alphainvest.modules.ai.domain.exceptions import (
    AIModelNotFoundError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.infrastructure.trend_model_loader import (
    TrendModelLoader,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_loads_registered_trend_version() -> None:
    model_id = uuid4()
    version_id = uuid4()

    version = SimpleNamespace(
        id=version_id,
        modelo_id=model_id,
    )

    model = SimpleNamespace(
        id=model_id,
        codigo="PREDICCION_TENDENCIA",
    )

    repository = SimpleNamespace(
        get_model_version=AsyncMock(
            return_value=version
        ),
        get_model=AsyncMock(
            return_value=model
        ),
    )

    loaded = SimpleNamespace(
        version_id=version_id
    )

    service = TrendModelRuntimeService(
        repository
    )

    with patch.object(
        TrendModelLoader,
        "load",
        return_value=loaded,
    ):
        result = await service.load_version(
            version_id=version_id
        )

    assert result is loaded


@pytest.mark.asyncio
async def test_rejects_missing_version() -> None:
    repository = SimpleNamespace(
        get_model_version=AsyncMock(
            return_value=None
        ),
    )

    service = TrendModelRuntimeService(
        repository
    )

    with pytest.raises(
        ModelVersionNotFoundError
    ):
        await service.load_version(
            version_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_missing_model() -> None:
    version = SimpleNamespace(
        modelo_id=uuid4()
    )

    repository = SimpleNamespace(
        get_model_version=AsyncMock(
            return_value=version
        ),
        get_model=AsyncMock(
            return_value=None
        ),
    )

    service = TrendModelRuntimeService(
        repository
    )

    with pytest.raises(
        AIModelNotFoundError
    ):
        await service.load_version(
            version_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_wrong_model_code() -> None:
    model_id = uuid4()

    version = SimpleNamespace(
        modelo_id=model_id
    )

    repository = SimpleNamespace(
        get_model_version=AsyncMock(
            return_value=version
        ),
        get_model=AsyncMock(
            return_value=SimpleNamespace(
                codigo="CLASIFICACION_RIESGO"
            )
        ),
    )

    service = TrendModelRuntimeService(
        repository
    )

    with pytest.raises(
        ValueError,
        match="PREDICCION_TENDENCIA",
    ):
        await service.load_version(
            version_id=uuid4()
        )