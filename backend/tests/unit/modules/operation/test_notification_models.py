import pytest
from sqlalchemy.orm import configure_mappers

from alphainvest.modules.operation.infrastructure.models import (
    NotificationModel,
)

pytestmark = pytest.mark.unit


def test_notification_mappers_configure() -> None:
    configure_mappers()


def test_notification_uses_operation_schema() -> None:
    assert (
        NotificationModel.__table__.schema
        == "operation"
    )


def test_notification_maps_expected_table() -> None:
    assert NotificationModel.__table__.schema == "operation"
    assert NotificationModel.__tablename__ == "notificaciones"


def test_notification_maps_expected_columns() -> None:
    assert {
        column.name
        for column in NotificationModel.__table__.columns
    } == {
        "id",
        "usuario_id",
        "tipo",
        "canal",
        "titulo",
        "mensaje",
        "prioridad",
        "estado",
        "datos",
        "fecha_creacion",
        "fecha_programada",
        "fecha_envio",
        "fecha_lectura",
        "intentos_envio",
        "ultimo_error",
        "referencia_tipo",
        "referencia_id",
    }


def test_notification_user_foreign_key() -> None:
    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key
        in NotificationModel.__table__.foreign_keys
    }

    assert "app_auth.usuarios.id" in foreign_keys