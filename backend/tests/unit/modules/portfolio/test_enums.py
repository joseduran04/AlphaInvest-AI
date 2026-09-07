import pytest

from alphainvest.modules.portfolio.domain.enums import (
    PortfolioStatus,
    PortfolioType,
    PositionStatus,
)

pytestmark = pytest.mark.unit


def test_portfolio_types_match_database() -> None:
    assert {
        item.value
        for item in PortfolioType
    } == {
        "VIRTUAL",
        "SIMULADO",
    }


def test_portfolio_statuses_match_database() -> None:
    assert {
        item.value
        for item in PortfolioStatus
    } == {
        "ACTIVO",
        "CERRADO",
        "ARCHIVADO",
    }


def test_position_statuses_match_database() -> None:
    assert {
        item.value
        for item in PositionStatus
    } == {
        "ABIERTA",
        "CERRADA",
    }