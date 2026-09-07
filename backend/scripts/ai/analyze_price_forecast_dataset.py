import asyncio
from datetime import date

import numpy as np

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.price_forecast_ml_adapter import (
    PriceForecastMLAdapter,
)
from alphainvest.modules.ai.application.price_forecast_target_service import (
    PriceForecastTargetService,
)
from alphainvest.modules.ai.application.price_forecast_temporal_split_service import (
    PriceForecastTemporalSplitService,
)
from alphainvest.modules.ai.domain.price_forecast_experiment import (
    PRICE_FORECAST_YAHOO_V1,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

SYMBOL = "AAPL"
SOURCE_NAME = "Yahoo Finance"

START_DATE = date(2000, 1, 1)
END_DATE = date(2026, 8, 14)


def print_statistics(
    *,
    name: str,
    values: np.ndarray,
) -> None:
    print()
    print(name)
    print("-" * 60)

    print(
        f"Rows:       {values.size}"
    )

    print(
        f"Mean:       {np.mean(values):.6f}%"
    )

    print(
        f"Median:     {np.median(values):.6f}%"
    )

    print(
        f"Std:        {np.std(values):.6f}%"
    )

    print(
        f"Minimum:    {np.min(values):.6f}%"
    )

    print(
        f"Maximum:    {np.max(values):.6f}%"
    )

    percentiles = (
        1,
        5,
        25,
        50,
        75,
        95,
        99,
    )

    percentile_values = np.percentile(
        values,
        percentiles,
    )

    for percentile, value in zip(
        percentiles,
        percentile_values,
        strict=True,
    ):
        print(
            f"P{percentile:02}:        "
            f"{value:.6f}%"
        )


async def analyze() -> None:
    configuration = PRICE_FORECAST_YAHOO_V1

    async with AsyncSessionFactory() as session:
        repository = MarketRepository(session)

        asset = (
            await repository
            .get_active_asset_by_symbol(
                SYMBOL
            )
        )

        if asset is None:
            raise RuntimeError(
                f"No existe el activo {SYMBOL}"
            )

        feature_service = AIFeatureDataService(
            market_repository=repository,
            source_name=SOURCE_NAME,
        )

        feature_dataset = (
            await feature_service.build_dataset(
                asset_id=asset.id,
                start_date=START_DATE,
                end_date=END_DATE,
            )
        )

        regression_dataset = (
            PriceForecastTargetService
            .build_training_dataset(
                dataset=feature_dataset,
                horizon_sessions=(
                    configuration
                    .horizon_sessions
                ),
            )
        )

        split = (
            PriceForecastTemporalSplitService
            .split(
                dataset=regression_dataset,
                train_ratio=(
                    configuration.train_ratio
                ),
                validation_ratio=(
                    configuration
                    .validation_ratio
                ),
            )
        )

        train = PriceForecastMLAdapter.transform(
            split.train
        )

        validation = (
            PriceForecastMLAdapter.transform(
                split.validation
            )
        )

        test = PriceForecastMLAdapter.transform(
            split.test
        )

        all_targets = np.asarray(
            [
                float(
                    row.target
                    .future_return_percentage
                )
                for row in regression_dataset.rows
            ],
            dtype=np.float64,
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — DIAGNÓSTICO "
            "PRONOSTICO_PRECIO"
        )
        print("=" * 72)

        print(f"Activo:          {asset.simbolo}")
        print(f"Fuente:          {SOURCE_NAME}")
        print(
            f"Feature rows:    "
            f"{feature_dataset.size}"
        )
        print(
            f"Targets:         "
            f"{regression_dataset.size}"
        )
        print(
            f"Horizonte:       "
            f"{configuration.horizon_sessions} "
            "sesiones"
        )

        print(
            f"Train:           {train.rows}"
        )
        print(
            f"Validation:      "
            f"{validation.rows}"
        )
        print(
            f"Test reservado:  {test.rows}"
        )
        print(
            f"Purge sessions:  "
            f"{split.purge_sessions}"
        )

        print_statistics(
            name="GLOBAL",
            values=all_targets,
        )

        print_statistics(
            name="TRAIN",
            values=train.targets,
        )

        print_statistics(
            name="VALIDATION",
            values=validation.targets,
        )

        print_statistics(
            name=(
                "TEST — ESTADÍSTICAS "
                "DESCRIPTIVAS ÚNICAMENTE"
            ),
            values=test.targets,
        )

        print()
        print("=" * 72)
        print(
            "TEST NO UTILIZADO PARA "
            "EVALUAR NINGÚN MODELO"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await analyze()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())