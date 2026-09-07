from alphainvest.modules.simulation.domain.historical import (
    HistoricalAlignedAsset,
    HistoricalAlignedSimulation,
    HistoricalPricePoint,
    HistoricalSimulationInput,
)


class HistoricalCalendarAligner:
    """Determina el periodo efectivo y calendario común."""

    @staticmethod
    def align(
        simulation: HistoricalSimulationInput,
    ) -> HistoricalAlignedSimulation:
        asset_start_dates = [
            asset.prices[0].date
            for asset in simulation.assets
        ]

        asset_end_dates = [
            asset.prices[-1].date
            for asset in simulation.assets
        ]

        effective_start_date = max(
            asset_start_dates
        )
        effective_end_date = min(
            asset_end_dates
        )

        if (
            effective_start_date
            > effective_end_date
        ):
            raise ValueError(
                "Los activos no tienen un periodo "
                "histórico común"
            )

        common_date_set = set(
            simulation.assets[0].prices[index].date
            for index in range(
                len(simulation.assets[0].prices)
            )
            if (
                effective_start_date
                <= simulation.assets[0].prices[index].date
                <= effective_end_date
            )
        )

        for asset in simulation.assets[1:]:
            asset_dates = {
                point.date
                for point in asset.prices
                if (
                    effective_start_date
                    <= point.date
                    <= effective_end_date
                )
            }

            common_date_set.intersection_update(
                asset_dates
            )

        common_dates = tuple(
            sorted(common_date_set)
        )

        if not common_dates:
            raise ValueError(
                "Los activos no comparten fechas "
                "de cotización"
            )

        effective_start_date = common_dates[0]
        effective_end_date = common_dates[-1]

        common_date_lookup = set(common_dates)

        aligned_assets = tuple(
            HistoricalAlignedAsset(
                asset_id=asset.asset_id,
                assigned_percentage=(
                    asset.assigned_percentage
                ),
                prices=tuple(
                    HistoricalPricePoint(
                        date=point.date,
                        price=point.price,
                    )
                    for point in asset.prices
                    if point.date in common_date_lookup
                ),
            )
            for asset in simulation.assets
        )

        return HistoricalAlignedSimulation(
            initial_capital=(
                simulation.initial_capital
            ),
            currency=simulation.currency,
            periodic_contribution=(
                simulation.periodic_contribution
            ),
            contribution_frequency=(
                simulation.contribution_frequency
            ),
            commission_percentage=(
                simulation.commission_percentage
            ),
            requested_start_date=(
                simulation.requested_start_date
            ),
            requested_end_date=(
                simulation.requested_end_date
            ),
            effective_start_date=(
                effective_start_date
            ),
            effective_end_date=(
                effective_end_date
            ),
            common_dates=common_dates,
            assets=aligned_assets,
            risk_free_rate=(
                simulation.risk_free_rate
            ),
        )