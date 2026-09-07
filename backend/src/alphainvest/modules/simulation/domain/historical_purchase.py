from decimal import Decimal

from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedSimulation,
    HistoricalInitialPortfolio,
    HistoricalInitialPosition,
)


class HistoricalInitialPurchaseCalculator:
    """Calcula la adquisición virtual inicial."""

    @staticmethod
    def calculate(
        simulation: HistoricalAlignedSimulation,
    ) -> HistoricalInitialPortfolio:
        positions = tuple(
            HistoricalInitialPurchaseCalculator
            ._build_position(
                simulation=simulation,
                asset_index=index,
            )
            for index in range(
                len(simulation.assets)
            )
        )

        total_commission = sum(
            (
                position.commission_amount
                for position in positions
            ),
            start=Decimal("0"),
        )

        return HistoricalInitialPortfolio(
            initial_capital=simulation.initial_capital,
            currency=simulation.currency,
            effective_start_date=(
                simulation.effective_start_date
            ),
            positions=positions,
            total_commission=total_commission,
        )

    @staticmethod
    def _build_position(
        *,
        simulation: HistoricalAlignedSimulation,
        asset_index: int,
    ) -> HistoricalInitialPosition:
        asset = simulation.assets[asset_index]

        allocated_capital = (
            simulation.initial_capital
            * asset.assigned_percentage
            / Decimal("100")
        )

        commission_rate = (
            simulation.commission_percentage
            / Decimal("100")
        )

        net_invested_capital = (
            allocated_capital
            / (
                Decimal("1")
                + commission_rate
            )
        )

        commission_amount = (
            allocated_capital
            - net_invested_capital
        )

        initial_price = asset.prices[0].price

        initial_quantity = (
            net_invested_capital
            / initial_price
        )

        return HistoricalInitialPosition(
            asset_id=asset.asset_id,
            assigned_percentage=(
                asset.assigned_percentage
            ),
            allocated_capital=allocated_capital,
            initial_price=initial_price,
            initial_quantity=initial_quantity,
            commission_amount=commission_amount,
        )