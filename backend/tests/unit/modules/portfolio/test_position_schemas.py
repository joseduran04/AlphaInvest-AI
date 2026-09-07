from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from alphainvest.modules.portfolio.presentation.schemas import (
    PositionCreateRequest,
    PositionUpdateRequest,
)

pytestmark = pytest.mark.unit


def test_position_create_accepts_valid_data() -> None:
    asset_id = uuid4()
    opening_date = datetime(
        2026,
        8,
        1,
        15,
        30,
        tzinfo=UTC,
    )

    request = PositionCreateRequest(
        activo_id=asset_id,
        cantidad=Decimal("10.50000000"),
        precio_promedio_compra=Decimal(
            "125.75000000"
        ),
        fecha_apertura=opening_date,
    )

    assert request.activo_id == asset_id
    assert request.cantidad == Decimal(
        "10.50000000"
    )
    assert (
        request.precio_promedio_compra
        == Decimal("125.75000000")
    )
    assert request.fecha_apertura == opening_date


@pytest.mark.parametrize(
    "quantity",
    [
        Decimal("0"),
        Decimal("-1"),
    ],
)
def test_position_create_rejects_non_positive_quantity(
    quantity: Decimal,
) -> None:
    with pytest.raises(ValidationError):
        PositionCreateRequest(
            activo_id=uuid4(),
            cantidad=quantity,
            precio_promedio_compra=Decimal(
                "100"
            ),
        )


@pytest.mark.parametrize(
    "purchase_price",
    [
        Decimal("0"),
        Decimal("-1"),
    ],
)
def test_position_create_rejects_non_positive_price(
    purchase_price: Decimal,
) -> None:
    with pytest.raises(ValidationError):
        PositionCreateRequest(
            activo_id=uuid4(),
            cantidad=Decimal("1"),
            precio_promedio_compra=(
                purchase_price
            ),
        )


def test_position_update_accepts_quantity() -> None:
    request = PositionUpdateRequest(
        cantidad=Decimal("15")
    )

    assert request.cantidad == Decimal("15")
    assert request.precio_promedio_compra is None


def test_position_update_accepts_purchase_price() -> None:
    request = PositionUpdateRequest(
        precio_promedio_compra=Decimal(
            "150.25"
        )
    )

    assert (
        request.precio_promedio_compra
        == Decimal("150.25")
    )
    assert request.cantidad is None


def test_position_update_rejects_empty_request() -> None:
    with pytest.raises(
        ValidationError,
        match="Debe enviar al menos un campo",
    ):
        PositionUpdateRequest()


def test_position_update_rejects_zero_quantity() -> None:
    with pytest.raises(ValidationError):
        PositionUpdateRequest(
            cantidad=Decimal("0")
        )


def test_position_update_rejects_zero_price() -> None:
    with pytest.raises(ValidationError):
        PositionUpdateRequest(
            precio_promedio_compra=Decimal(
                "0"
            )
        )