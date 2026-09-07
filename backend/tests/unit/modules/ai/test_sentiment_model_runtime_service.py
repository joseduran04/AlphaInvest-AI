from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from alphainvest.modules.ai.application.sentiment_model_runtime_service import (
    SentimentModelRuntimeService,
)
from alphainvest.modules.ai.domain.exceptions import (
    AIModelNotFoundError,
    ModelVersionNotFoundError,
)
from alphainvest.modules.ai.infrastructure.sentiment_model_loader import (
    SentimentModelLoader,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_loads_registered_sentiment_version(
) -> None:
    model_id = uuid4()
    version_id = uuid4()

    version = SimpleNamespace(
        id=version_id,
        modelo_id=model_id,
    )

    model = SimpleNamespace(
        id=model_id,
        codigo="ANALISIS_SENTIMIENTO",
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

    service = (
        SentimentModelRuntimeService(
            repository
        )
    )

    with patch.object(
        SentimentModelLoader,
        "load",
        return_value=loaded,
    ):
        result = (
            await service
            .load_version(
                version_id=version_id
            )
        )

    assert result is loaded


@pytest.mark.asyncio
async def test_rejects_missing_version(
) -> None:
    repository = SimpleNamespace(
        get_model_version=AsyncMock(
            return_value=None
        ),
    )

    service = (
        SentimentModelRuntimeService(
            repository
        )
    )

    with pytest.raises(
        ModelVersionNotFoundError
    ):
        await service.load_version(
            version_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_missing_model(
) -> None:
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

    service = (
        SentimentModelRuntimeService(
            repository
        )
    )

    with pytest.raises(
        AIModelNotFoundError
    ):
        await service.load_version(
            version_id=uuid4()
        )


@pytest.mark.asyncio
async def test_rejects_wrong_model_code(
) -> None:
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
                codigo="PREDICCION_TENDENCIA"
            )
        ),
    )

    service = (
        SentimentModelRuntimeService(
            repository
        )
    )

    with pytest.raises(
        ValueError,
        match="ANALISIS_SENTIMIENTO",
    ):
        await service.load_version(
            version_id=uuid4()
        )