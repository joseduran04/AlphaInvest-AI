from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAssetInput,
    HistoricalPricePoint,
    HistoricalSimulationInput,
)

pytestmark = pytest.mark.unit


def build_price(
    *,
    price_date: date = date(2024, 1, 2),
    price: Decimal = Decimal("100"),
) -> HistoricalPricePoint:
    return HistoricalPricePoint(
        date=price_date,
        price=price,
    )


def build_asset(
    *,
    percentage: Decimal = Decimal("100"),
) -> HistoricalAssetInput:
    return HistoricalAssetInput(
        asset_id=uuid4(),
        assigned_percentage=percentage,
        prices=(
            build_price(),
        ),
    )


def test_historical_price_accepts_positive_price(
) -> None:
    point = build_price(
        price=Decimal("125.50")
    )

    assert point.price == Decimal("125.50")


def test_historical_price_rejects_zero_price(
) -> None:
    with pytest.raises(
        ValueError,
        match="mayor que cero",
    ):
        build_price(
            price=Decimal("0")
        )


def test_historical_price_rejects_negative_price(
) -> None:
    with pytest.raises(
        ValueError,
        match="mayor que cero",
    ):
        build_price(
            price=Decimal("-1")
        )


def test_asset_accepts_valid_price_series(
) -> None:
    asset = HistoricalAssetInput(
        asset_id=uuid4(),
        assigned_percentage=Decimal("100"),
        prices=(
            build_price(
                price_date=date(2024, 1, 2)
            ),
            build_price(
                price_date=date(2024, 1, 3)
            ),
        ),
    )

    assert len(asset.prices) == 2


def test_asset_rejects_empty_price_series(
) -> None:
    with pytest.raises(
        ValueError,
        match="precios históricos",
    ):
        HistoricalAssetInput(
            asset_id=uuid4(),
            assigned_percentage=Decimal("100"),
            prices=(),
        )


def test_asset_rejects_invalid_percentage(
) -> None:
    with pytest.raises(
        ValueError,
        match="porcentaje asignado",
    ):
        build_asset(
            percentage=Decimal("0")
        )


def test_asset_rejects_unsorted_prices(
) -> None:
    with pytest.raises(
        ValueError,
        match="cronológicamente",
    ):
        HistoricalAssetInput(
            asset_id=uuid4(),
            assigned_percentage=Decimal("100"),
            prices=(
                build_price(
                    price_date=date(2024, 1, 3)
                ),
                build_price(
                    price_date=date(2024, 1, 2)
                ),
            ),
        )


def test_asset_rejects_duplicate_price_dates(
) -> None:
    with pytest.raises(
        ValueError,
        match="duplicados",
    ):
        HistoricalAssetInput(
            asset_id=uuid4(),
            assigned_percentage=Decimal("100"),
            prices=(
                build_price(
                    price_date=date(2024, 1, 2),
                    price=Decimal("100"),
                ),
                build_price(
                    price_date=date(2024, 1, 2),
                    price=Decimal("101"),
                ),
            ),
        )


def test_simulation_input_accepts_valid_data(
) -> None:
    first_asset = build_asset(
        percentage=Decimal("60")
    )
    second_asset = build_asset(
        percentage=Decimal("40")
    )

    simulation = HistoricalSimulationInput(
        initial_capital=Decimal("10000"),
        currency="usd",
        requested_start_date=date(2024, 1, 1),
        requested_end_date=date(2024, 12, 31),
        assets=(
            first_asset,
            second_asset,
        ),
    )

    assert (
        simulation.initial_capital
        == Decimal("10000")
    )
    assert simulation.currency == "USD"
    assert len(simulation.assets) == 2


def test_simulation_input_rejects_non_positive_capital(
) -> None:
    with pytest.raises(
        ValueError,
        match="capital inicial",
    ):
        HistoricalSimulationInput(
            initial_capital=Decimal("0"),
            currency="USD",
            requested_start_date=date(2024, 1, 1),
            requested_end_date=date(2024, 12, 31),
            assets=(
                build_asset(),
            ),
        )


def test_simulation_input_rejects_invalid_dates(
) -> None:
    with pytest.raises(
        ValueError,
        match="fecha final",
    ):
        HistoricalSimulationInput(
            initial_capital=Decimal("10000"),
            currency="USD",
            requested_start_date=date(2024, 12, 31),
            requested_end_date=date(2024, 1, 1),
            assets=(
                build_asset(),
            ),
        )


def test_simulation_input_rejects_invalid_currency(
) -> None:
    with pytest.raises(
        ValueError,
        match="únicamente letras",
    ):
        HistoricalSimulationInput(
            initial_capital=Decimal("10000"),
            currency="U1D",
            requested_start_date=date(2024, 1, 1),
            requested_end_date=date(2024, 12, 31),
            assets=(
                build_asset(),
            ),
        )


def test_simulation_input_rejects_empty_assets(
) -> None:
    with pytest.raises(
        ValueError,
        match="al menos un activo",
    ):
        HistoricalSimulationInput(
            initial_capital=Decimal("10000"),
            currency="USD",
            requested_start_date=date(2024, 1, 1),
            requested_end_date=date(2024, 12, 31),
            assets=(),
        )


def test_simulation_input_requires_100_percent_distribution(
) -> None:
    with pytest.raises(
        ValueError,
        match="sumar 100",
    ):
        HistoricalSimulationInput(
            initial_capital=Decimal("10000"),
            currency="USD",
            requested_start_date=date(2024, 1, 1),
            requested_end_date=date(2024, 12, 31),
            assets=(
                build_asset(
                    percentage=Decimal("60")
                ),
            ),
        )


def test_simulation_input_rejects_duplicate_assets(
) -> None:
    asset_id = uuid4()

    first_asset = HistoricalAssetInput(
        asset_id=asset_id,
        assigned_percentage=Decimal("50"),
        prices=(
            build_price(),
        ),
    )

    second_asset = HistoricalAssetInput(
        asset_id=asset_id,
        assigned_percentage=Decimal("50"),
        prices=(
            build_price(),
        ),
    )

    with pytest.raises(
        ValueError,
        match="no puede repetirse",
    ):
        HistoricalSimulationInput(
            initial_capital=Decimal("10000"),
            currency="USD",
            requested_start_date=date(2024, 1, 1),
            requested_end_date=date(2024, 12, 31),
            assets=(
                first_asset,
                second_asset,
            ),
        )