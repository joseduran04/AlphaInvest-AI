import pytest

from alphainvest.modules.ai.domain.enums import (
    AIModelStatus,
)

pytestmark = pytest.mark.unit


def test_ai_model_status_values() -> None:
    assert AIModelStatus.DEVELOPMENT.value == "DESARROLLO"
    assert AIModelStatus.VALIDATION.value == "VALIDACION"
    assert AIModelStatus.ACTIVE.value == "ACTIVO"
    assert AIModelStatus.INACTIVE.value == "INACTIVO"
    assert AIModelStatus.RETIRED.value == "RETIRADO"


def test_ai_model_status_is_string_enum() -> None:
    assert AIModelStatus.ACTIVE == "ACTIVO"