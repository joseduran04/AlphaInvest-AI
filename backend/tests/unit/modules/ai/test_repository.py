from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)

pytestmark = pytest.mark.unit


def build_session() -> MagicMock:
    session = MagicMock()

    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()

    return session


@pytest.mark.asyncio
async def test_list_models() -> None:
    session = build_session()

    model = SimpleNamespace(
        id=uuid4(),
        codigo="PREDICCION_TENDENCIA",
    )

    models_result = MagicMock()
    models_result.scalars.return_value.all.return_value = [
        model
    ]

    count_result = MagicMock()
    count_result.scalar_one.return_value = 1

    session.execute.side_effect = [
        models_result,
        count_result,
    ]

    repository = AIRepository(session)

    models, total = await repository.list_models(
        search=None,
        model_type=None,
        status=None,
        limit=20,
        offset=0,
    )

    assert models == [model]
    assert total == 1
    assert session.execute.await_count == 2


@pytest.mark.asyncio
async def test_get_model() -> None:
    session = build_session()

    model = SimpleNamespace(
        id=uuid4(),
        codigo="CLASIFICACION_RIESGO",
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = model
    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.get_model(
        model.id
    )

    assert response is model
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_model_returns_none() -> None:
    session = build_session()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.get_model(
        uuid4()
    )

    assert response is None


@pytest.mark.asyncio
async def test_get_model_by_code() -> None:
    session = build_session()

    model = SimpleNamespace(
        id=uuid4(),
        codigo="PREDICCION_TENDENCIA",
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = model
    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.get_model_by_code(
        "prediccion_tendencia"
    )

    assert response is model


@pytest.mark.asyncio
async def test_get_model_version() -> None:
    session = build_session()

    version = SimpleNamespace(
        id=uuid4(),
        activa=True,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = version
    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.get_model_version(
        version.id
    )

    assert response is version
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_model_version_returns_none(
) -> None:
    session = build_session()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.get_model_version(
        uuid4()
    )

    assert response is None


@pytest.mark.asyncio
async def test_get_active_model_version() -> None:
    session = build_session()

    version = SimpleNamespace(
        id=uuid4(),
        activa=True,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = version
    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository.get_active_model_version(
            version.id
        )
    )

    assert response is version
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_active_model_version_returns_none(
) -> None:
    session = build_session()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository.get_active_model_version(
            uuid4()
        )
    )

    assert response is None


@pytest.mark.asyncio
async def test_list_model_versions() -> None:
    session = build_session()

    model_id = uuid4()

    versions = [
        SimpleNamespace(
            id=uuid4(),
            modelo_id=model_id,
            version="1.0.0",
        ),
        SimpleNamespace(
            id=uuid4(),
            modelo_id=model_id,
            version="0.9.0",
        ),
    ]

    result = MagicMock()
    result.scalars.return_value.all.return_value = (
        versions
    )

    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.list_model_versions(
        model_id=model_id
    )

    assert response == versions
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_active_version_for_model() -> None:
    session = build_session()

    model_id = uuid4()

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=model_id,
        activa=True,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = version
    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository.get_active_version_for_model(
            model_id
        )
    )

    assert response is version


@pytest.mark.asyncio
async def test_get_active_version_for_model_returns_none(
) -> None:
    session = build_session()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository.get_active_version_for_model(
            uuid4()
        )
    )

    assert response is None


@pytest.mark.asyncio
async def test_get_active_version_by_model_code() -> None:
    session = build_session()

    version = SimpleNamespace(
        id=uuid4(),
        activa=True,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = version
    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository.get_active_version_by_model_code(
            "prediccion_tendencia"
        )
    )

    assert response is version


@pytest.mark.asyncio
async def test_get_active_version_by_model_code_returns_none(
) -> None:
    session = build_session()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository.get_active_version_by_model_code(
            "clasificacion_riesgo"
        )
    )

    assert response is None


@pytest.mark.asyncio
async def test_activate_model_version() -> None:
    session = build_session()

    model_id = uuid4()

    previous = SimpleNamespace(
        id=uuid4(),
        modelo_id=model_id,
        activa=True,
        fecha_activacion=datetime.now(UTC),
        fecha_desactivacion=None,
    )

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=model_id,
        activa=False,
        fecha_activacion=None,
        fecha_desactivacion=None,
    )

    active_result = MagicMock()
    active_result.scalar_one_or_none.return_value = (
        previous
    )

    session.execute.return_value = active_result
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    repository = AIRepository(session)

    response = (
        await repository.activate_model_version(
            version
        )
    )

    assert response is version

    assert previous.activa is False
    assert previous.fecha_desactivacion is not None

    assert version.activa is True
    assert version.fecha_activacion is not None
    assert version.fecha_desactivacion is None

    assert session.flush.await_count == 2
    session.refresh.assert_awaited_once_with(version)


@pytest.mark.asyncio
async def test_activate_already_active_version_is_idempotent(
) -> None:
    session = build_session()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        activa=True,
        fecha_activacion=datetime.now(UTC),
        fecha_desactivacion=None,
    )

    repository = AIRepository(session)

    response = (
        await repository.activate_model_version(
            version
        )
    )

    assert response is version
    session.flush.assert_not_awaited()
    session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_deactivate_model_version() -> None:
    session = build_session()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        activa=True,
        fecha_activacion=datetime.now(UTC),
        fecha_desactivacion=None,
    )

    repository = AIRepository(session)

    response = (
        await repository.deactivate_model_version(
            version
        )
    )

    assert response is version
    assert version.activa is False
    assert version.fecha_desactivacion is not None

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(version)


@pytest.mark.asyncio
async def test_deactivate_inactive_version_is_idempotent(
) -> None:
    session = build_session()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        activa=False,
        fecha_activacion=None,
        fecha_desactivacion=None,
    )

    repository = AIRepository(session)

    response = (
        await repository.deactivate_model_version(
            version
        )
    )

    assert response is version
    session.flush.assert_not_awaited()
    session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_analysis_request() -> None:
    session = build_session()

    repository = AIRepository(session)

    user_id = uuid4()
    portfolio_id = uuid4()
    risk_profile_id = uuid4()
    simulation_execution_id = uuid4()

    response = await repository.create_analysis_request(
        user_id=user_id,
        analysis_type="ACTIVO",
        horizon="CORTO_PLAZO",
        reference_date=date(2026, 8, 14),
        parameters={
            "asset_id": str(uuid4()),
        },
        portfolio_id=portfolio_id,
        risk_profile_id=risk_profile_id,
        simulation_execution_id=(
            simulation_execution_id
        ),
        process_identifier="ai-test-process",
    )

    assert response.usuario_id == user_id
    assert response.portafolio_id == portfolio_id

    assert (
        response.perfil_riesgo_id
        == risk_profile_id
    )

    assert (
        response.ejecucion_simulacion_id
        == simulation_execution_id
    )

    assert response.tipo_analisis == "ACTIVO"
    assert response.horizonte == "CORTO_PLAZO"

    assert (
        response.fecha_referencia
        == date(2026, 8, 14)
    )

    assert response.estado == "PENDIENTE"

    assert (
        response.identificador_proceso
        == "ai-test-process"
    )

    session.add.assert_called_once_with(
        response
    )

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        response
    )


@pytest.mark.asyncio
async def test_get_analysis_request() -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        estado="PENDIENTE",
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = request

    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.get_analysis_request(
        request.id
    )

    assert response is request

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_analysis_request_returns_none() -> None:
    session = build_session()

    result = MagicMock()
    result.scalar_one_or_none.return_value = None

    session.execute.return_value = result

    repository = AIRepository(session)

    response = await repository.get_analysis_request(
        uuid4()
    )

    assert response is None


@pytest.mark.asyncio
async def test_update_analysis_request_status() -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        estado="PENDIENTE",
        porcentaje_progreso=Decimal("0"),
        mensaje_error=None,
    )

    repository = AIRepository(session)

    response = (
        await repository
        .update_analysis_request_status(
            request,
            status="EJECUTANDO",
            progress=Decimal("25"),
            error_message=None,
        )
    )

    assert response is request
    assert request.estado == "EJECUTANDO"

    assert (
        request.porcentaje_progreso
        == Decimal("25")
    )

    assert request.mensaje_error is None

    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(
        request
    )


@pytest.mark.asyncio
async def test_update_analysis_request_failure() -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        estado="EJECUTANDO",
        porcentaje_progreso=Decimal("50"),
        mensaje_error=None,
    )

    repository = AIRepository(session)

    response = (
        await repository
        .update_analysis_request_status(
            request,
            status="FALLIDA",
            progress=Decimal("50"),
            error_message=(
                "Error durante análisis"
            ),
        )
    )

    assert response.estado == "FALLIDA"

    assert (
        response.mensaje_error
        == "Error durante análisis"
    )

    assert (
        response.porcentaje_progreso
        == Decimal("50")
    )


@pytest.mark.asyncio
async def test_get_analysis_request_for_user() -> None:
    session = build_session()

    request_id = uuid4()
    user_id = uuid4()

    request = SimpleNamespace(
        id=request_id,
        usuario_id=user_id,
    )

    result = MagicMock()
    result.scalar_one_or_none.return_value = request

    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository
        .get_analysis_request_for_user(
            request_id=request_id,
            user_id=user_id,
        )
    )

    assert response is request

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_lists_pending_asset_analysis_requests() -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="ACTIVO",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
    )

    result = MagicMock()

    result.scalars.return_value.all.return_value = [
        request
    ]

    session.execute.return_value = result

    repository = AIRepository(session)

    response = (
        await repository
        .list_pending_asset_analysis_requests(
            limit=20
        )
    )

    assert response == [request]

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_increments_analysis_request_attempt() -> None:
    session = build_session()

    request = SimpleNamespace(
        intentos_procesamiento=1
    )

    repository = AIRepository(session)

    result = await (
        repository
        .increment_analysis_request_attempt(
            request
        )
    )

    assert result == 2

    assert (
        request.intentos_procesamiento
        == 2
    )


@pytest.mark.asyncio
async def test_resets_analysis_request_for_retry() -> None:
    session = build_session()

    request = SimpleNamespace(
        estado="EJECUTANDO",
        porcentaje_progreso=Decimal("10"),
        fecha_inicio=datetime.now(UTC),
        fecha_fin=None,
        mensaje_error=None,
        identificador_proceso="worker-test",
        intentos_procesamiento=2,
    )

    repository = AIRepository(session)

    result = await (
        repository
        .reset_analysis_request_for_retry(
            request
        )
    )

    assert result.estado == "PENDIENTE"

    assert (
        result.porcentaje_progreso
        == Decimal("0")
    )

    assert result.fecha_inicio is None
    assert result.fecha_fin is None
    assert result.mensaje_error is None

    assert (
        result.identificador_proceso
        is None
    )

    assert (
        result.intentos_procesamiento
        == 2
    )


@pytest.mark.asyncio
async def test_creates_sentiment_analysis() -> None:
    session = build_session()

    request_id = uuid4()
    asset_id = uuid4()
    news_reference_id = uuid4()
    version_model_id = uuid4()

    repository = AIRepository(
        session
    )

    result = await (
        repository
        .create_sentiment_analysis(
            request_id=request_id,
            asset_id=asset_id,
            news_reference_id=(
                news_reference_id
            ),
            version_model_id=(
                version_model_id
            ),
            source_type="NOTICIA",
            source_identifier="mongo-test-123",
            sentiment="POSITIVO",
            score=Decimal("0.70"),
            confidence=Decimal("0.80"),
            positive_probability=(
                Decimal("0.80")
            ),
            neutral_probability=(
                Decimal("0.10")
            ),
            negative_probability=(
                Decimal("0.10")
            ),
            relevance=Decimal("0.95"),
            language="en",
            detected_entities={
                "tickers": [
                    "AAPL"
                ]
            },
            summary=(
                "Apple reported "
                "strong financial results."
            ),
            content_date=datetime(
                2026,
                8,
                27,
                tzinfo=UTC,
            ),
        )
    )

    session.add.assert_called_once()

    added = (
        session.add
        .call_args
        .args[0]
    )

    assert result is added

    assert (
        added.solicitud_id
        == request_id
    )

    assert (
        added.activo_id
        == asset_id
    )

    assert (
        added.noticia_referencia_id
        == news_reference_id
    )

    assert (
        added.version_modelo_id
        == version_model_id
    )

    assert (
        added.tipo_fuente
        == "NOTICIA"
    )

    assert (
        added.identificador_fuente
        == "mongo-test-123"
    )

    assert (
        added.sentimiento
        == "POSITIVO"
    )

    assert (
        added.puntuacion
        == Decimal("0.70")
    )

    assert (
        added.confianza
        == Decimal("0.80")
    )

    assert (
        added.probabilidad_positiva
        == Decimal("0.80")
    )

    assert (
        added.probabilidad_neutral
        == Decimal("0.10")
    )

    assert (
        added.probabilidad_negativa
        == Decimal("0.10")
    )

    assert (
        added.relevancia
        == Decimal("0.95")
    )

    assert added.idioma == "en"

    assert (
        added.entidades_detectadas
        == {
            "tickers": [
                "AAPL"
            ]
        }
    )

    assert (
        added.resumen
        == (
            "Apple reported "
            "strong financial results."
        )
    )

    session.flush.assert_awaited_once()

    session.refresh.assert_awaited_once_with(
        added
    )


@pytest.mark.asyncio
async def test_gets_sentiment_analysis_by_request_and_news(
) -> None:
    session = build_session()

    request_id = uuid4()
    news_reference_id = uuid4()

    analysis = SimpleNamespace(
        id=uuid4(),
        solicitud_id=request_id,
        noticia_referencia_id=(
            news_reference_id
        ),
    )

    result = MagicMock()

    (
        result
        .scalar_one_or_none
        .return_value
    ) = analysis

    session.execute.return_value = (
        result
    )

    repository = AIRepository(
        session
    )

    response = await (
        repository
        .get_sentiment_analysis_by_request_and_news(
            request_id=request_id,
            news_reference_id=(
                news_reference_id
            ),
        )
    )

    assert response is analysis

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_lists_pending_sentiment_analysis_requests(
) -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="SENTIMIENTO",
        estado="PENDIENTE",
        horizonte=None,
    )

    result = MagicMock()

    result.scalars.return_value.all.return_value = [
        request
    ]

    session.execute.return_value = result

    repository = AIRepository(
        session
    )

    response = await (
        repository
        .list_pending_sentiment_analysis_requests(
            limit=20
        )
    )

    assert response == [
        request
    ]

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_lists_running_sentiment_analysis_requests(
) -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="SENTIMIENTO",
        estado="EJECUTANDO",
        horizonte=None,
    )

    result = MagicMock()

    result.scalars.return_value.all.return_value = [
        request
    ]

    session.execute.return_value = result

    repository = AIRepository(
        session
    )

    response = await (
        repository
        .list_running_sentiment_analysis_requests(
            limit=20
        )
    )

    assert response == [
        request
    ]

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_lists_pending_integral_analysis_requests(
) -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="INTEGRAL",
        estado="PENDIENTE",
        horizonte="CORTO_PLAZO",
    )

    result = MagicMock()

    result.scalars.return_value.all.return_value = [
        request
    ]

    session.execute.return_value = result

    repository = AIRepository(
        session
    )

    response = await (
        repository
        .list_pending_integral_analysis_requests(
            limit=20
        )
    )

    assert response == [
        request
    ]

    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_lists_running_integral_analysis_requests(
) -> None:
    session = build_session()

    request = SimpleNamespace(
        id=uuid4(),
        tipo_analisis="INTEGRAL",
        estado="EJECUTANDO",
        horizonte="CORTO_PLAZO",
    )

    result = MagicMock()

    result.scalars.return_value.all.return_value = [
        request
    ]

    session.execute.return_value = result

    repository = AIRepository(
        session
    )

    response = await (
        repository
        .list_running_integral_analysis_requests(
            limit=20
        )
    )

    assert response == [
        request
    ]

    session.execute.assert_awaited_once()