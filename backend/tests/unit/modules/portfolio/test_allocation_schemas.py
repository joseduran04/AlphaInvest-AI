from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.portfolio.presentation.schemas import (
    AssetAllocationItemResponse,
    AssetAllocationResponse,
    SectorAllocationItemResponse,
    SectorAllocationResponse,
)

pytestmark = pytest.mark.unit


def test_asset_allocation_response() -> None:
    portfolio_id = uuid4()
    asset_id = uuid4()

    response = AssetAllocationResponse(
        portafolio_id=portfolio_id,
        moneda_base="USD",
        valor_total_distribuido=Decimal("1500"),
        items=[
            AssetAllocationItemResponse(
                activo_id=asset_id,
                simbolo="ORCL",
                nombre="Oracle Corporation",
                sector="Technology",
                industria="Software",
                cantidad=Decimal("10"),
                valor_referencia=Decimal("1500"),
                porcentaje=Decimal("100"),
            )
        ],
    )

    assert response.portafolio_id == portfolio_id
    assert response.items[0].activo_id == asset_id
    assert response.items[0].porcentaje == Decimal(
        "100"
    )


def test_asset_allocation_allows_empty_items() -> None:
    response = AssetAllocationResponse(
        portafolio_id=uuid4(),
        moneda_base="USD",
        valor_total_distribuido=Decimal("0"),
        items=[],
    )

    assert response.items == []
    assert (
        response.valor_total_distribuido
        == Decimal("0")
    )


def test_sector_allocation_response() -> None:
    response = SectorAllocationResponse(
        portafolio_id=uuid4(),
        moneda_base="USD",
        valor_total_distribuido=Decimal("2000"),
        items=[
            SectorAllocationItemResponse(
                sector="Technology",
                posiciones=2,
                valor_referencia=Decimal("2000"),
                porcentaje=Decimal("100"),
            )
        ],
    )

    assert response.items[0].sector == "Technology"
    assert response.items[0].posiciones == 2


def test_sector_allocation_supports_unknown_sector(
) -> None:
    item = SectorAllocationItemResponse(
        sector="SIN_SECTOR",
        posiciones=1,
        valor_referencia=Decimal("500"),
        porcentaje=Decimal("25"),
    )

    assert item.sector == "SIN_SECTOR"