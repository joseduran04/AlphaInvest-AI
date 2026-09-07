import pytest
from sqlalchemy.orm import configure_mappers

from alphainvest.modules.portfolio.infrastructure.models import (
    PortfolioModel,
    PortfolioValuationModel,
    PositionModel,
    WatchlistAssetModel,
    WatchlistModel,
)

pytestmark = pytest.mark.unit


def test_portfolio_mappers_configure() -> None:
    configure_mappers()


def test_models_use_portfolio_schema() -> None:
    models = [
        WatchlistModel,
        WatchlistAssetModel,
        PortfolioModel,
        PositionModel,
        PortfolioValuationModel,
    ]

    assert all(
        model.__table__.schema == "portfolio"
        for model in models
    )


def test_models_map_expected_tables() -> None:
    assert (
        WatchlistModel.__table__.fullname
        == "portfolio.listas_seguimiento"
    )
    assert (
        WatchlistAssetModel.__table__.fullname
        == "portfolio.lista_activos"
    )
    assert (
        PortfolioModel.__table__.fullname
        == "portfolio.portafolios"
    )
    assert (
        PositionModel.__table__.fullname
        == "portfolio.posiciones"
    )
    assert (
        PortfolioValuationModel.__table__.fullname
        == "portfolio.valoraciones_portafolio"
    )


def test_portfolio_has_unique_user_name() -> None:
    constraint_names = {
        constraint.name
        for constraint
        in PortfolioModel.__table__.constraints
    }

    assert (
        "uq_portafolios_usuario_nombre"
        in constraint_names
    )


def test_position_has_unique_asset_per_portfolio() -> None:
    constraint_names = {
        constraint.name
        for constraint
        in PositionModel.__table__.constraints
    }

    assert (
        "uq_posiciones_portafolio_activo"
        in constraint_names
    )