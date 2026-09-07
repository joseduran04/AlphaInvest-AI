import pytest

from alphainvest.modules.operation.domain.enums import (
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
    NotificationType,
)

pytestmark = pytest.mark.unit


def test_notification_types_match_database() -> None:
    assert {
        item.value
        for item in NotificationType
    } == {
        "SISTEMA",
        "SEGURIDAD",
        "ALERTA_PRECIO",
        "SIMULACION",
        "ANALISIS_IA",
        "RECOMENDACION",
        "PORTAFOLIO",
        "MANTENIMIENTO",
        "OTRA",
    }


def test_notification_channels_match_database() -> None:
    assert {
        item.value
        for item in NotificationChannel
    } == {
        "APLICACION",
        "CORREO",
        "PUSH",
    }


def test_notification_priorities_match_database() -> None:
    assert {
        item.value
        for item in NotificationPriority
    } == {
        "BAJA",
        "NORMAL",
        "ALTA",
        "URGENTE",
    }


def test_notification_statuses_match_database() -> None:
    assert {
        item.value
        for item in NotificationStatus
    } == {
        "PENDIENTE",
        "PROGRAMADA",
        "ENVIANDO",
        "ENVIADA",
        "FALLIDA",
        "CANCELADA",
    }