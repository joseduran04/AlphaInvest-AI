from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from alphainvest.modules.profile.application.service import (
    ProfileService,
)
from alphainvest.modules.profile.domain.enums import (
    RiskClassification,
)
from alphainvest.modules.profile.domain.exceptions import (
    QuestionnaireNotFoundError,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_active_questionnaire_not_found() -> None:
    repository = SimpleNamespace(
        get_published_questionnaire=AsyncMock(
            return_value=None
        )
    )
    service = ProfileService(repository)

    with pytest.raises(
        QuestionnaireNotFoundError,
        match="No existe un cuestionario publicado",
    ):
        await service.get_active_questionnaire()


@pytest.mark.asyncio
async def test_active_questionnaire_filters_inactive_content() -> None:
    active_option = SimpleNamespace(
        id=uuid4(),
        activa=True,
    )
    inactive_option = SimpleNamespace(
        id=uuid4(),
        activa=False,
    )

    active_question = SimpleNamespace(
        id=uuid4(),
        activa=True,
        opciones=[
            active_option,
            inactive_option,
        ],
    )
    inactive_question = SimpleNamespace(
        id=uuid4(),
        activa=False,
        opciones=[],
    )

    questionnaire = SimpleNamespace(
        preguntas=[
            active_question,
            inactive_question,
        ]
    )

    repository = SimpleNamespace(
        get_published_questionnaire=AsyncMock(
            return_value=questionnaire
        )
    )
    service = ProfileService(repository)

    result = await service.get_active_questionnaire()

    assert result is questionnaire
    assert result.preguntas == [active_question]
    assert result.preguntas[0].opciones == [
        active_option
    ]


@pytest.mark.asyncio
async def test_current_profile_returns_none_when_missing() -> None:
    user_id = uuid4()

    repository = SimpleNamespace(
        get_current_profile=AsyncMock(
            return_value=None
        )
    )
    service = ProfileService(repository)

    result = await service.get_current_risk_profile(
        user_id=user_id
    )

    assert result is None
    repository.get_current_profile.assert_awaited_once_with(
        user_id
    )


@pytest.mark.asyncio
async def test_current_profile_is_mapped_to_response() -> None:
    user_id = uuid4()
    profile_id = uuid4()
    evaluation_id = uuid4()
    started_at = datetime.now(UTC)

    profile = SimpleNamespace(
        id=profile_id,
        evaluacion_id=evaluation_id,
        clasificacion="MODERADO",
        puntuacion=Decimal("50.00"),
        confianza=Decimal("1.00"),
        descripcion="Perfil moderado",
        vigente=True,
        fecha_inicio=started_at,
    )

    repository = SimpleNamespace(
        get_current_profile=AsyncMock(
            return_value=profile
        )
    )
    service = ProfileService(repository)

    result = await service.get_current_risk_profile(
        user_id=user_id
    )

    assert result is not None
    assert result.id == profile_id
    assert result.evaluation_id == evaluation_id
    assert (
        result.classification
        == RiskClassification.MODERATE
    )
    assert result.score == Decimal("50.00")
    assert result.confidence == Decimal("1.00")
    assert result.description == "Perfil moderado"
    assert result.current is True
    assert result.started_at == started_at


@pytest.mark.asyncio
async def test_empty_profile_history_is_returned() -> None:
    user_id = uuid4()

    repository = SimpleNamespace(
        get_profile_history=AsyncMock(
            return_value=[]
        )
    )
    service = ProfileService(repository)

    result = await service.get_risk_profile_history(
        user_id=user_id
    )

    assert result.items == []
    assert result.total == 0
    repository.get_profile_history.assert_awaited_once_with(
        user_id
    )


@pytest.mark.asyncio
async def test_profile_history_is_mapped_to_response() -> None:
    user_id = uuid4()
    current_started_at = datetime.now(UTC)
    previous_started_at = datetime(
        2026,
        7,
        20,
        tzinfo=UTC,
    )
    previous_ended_at = datetime(
        2026,
        7,
        27,
        tzinfo=UTC,
    )

    current_profile = SimpleNamespace(
        id=uuid4(),
        evaluacion_id=uuid4(),
        clasificacion="MODERADO",
        puntuacion=Decimal("50.00"),
        confianza=Decimal("1.00"),
        descripcion="Perfil vigente",
        vigente=True,
        fecha_inicio=current_started_at,
        fecha_fin=None,
    )

    previous_profile = SimpleNamespace(
        id=uuid4(),
        evaluacion_id=uuid4(),
        clasificacion="CONSERVADOR",
        puntuacion=Decimal("15.00"),
        confianza=Decimal("1.00"),
        descripcion="Perfil anterior",
        vigente=False,
        fecha_inicio=previous_started_at,
        fecha_fin=previous_ended_at,
    )

    repository = SimpleNamespace(
        get_profile_history=AsyncMock(
            return_value=[
                current_profile,
                previous_profile,
            ]
        )
    )
    service = ProfileService(repository)

    result = await service.get_risk_profile_history(
        user_id=user_id
    )

    assert result.total == 2
    assert len(result.items) == 2

    assert result.items[0].current is True
    assert (
        result.items[0].classification
        == RiskClassification.MODERATE
    )
    assert result.items[0].ended_at is None

    assert result.items[1].current is False
    assert (
        result.items[1].classification
        == RiskClassification.CONSERVATIVE
    )
    assert (
        result.items[1].ended_at
        == previous_ended_at
    )