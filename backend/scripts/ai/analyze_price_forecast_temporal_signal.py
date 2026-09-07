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
from alphainvest.modules.ai.application.price_forecast_target_service import (
    PriceForecastTargetService,
)
from alphainvest.modules.ai.application.price_forecast_temporal_feature_service import (
    PriceForecastTemporalFeatureService,
)
from alphainvest.modules.ai.application.price_forecast_temporal_feature_split_service import (
    PriceForecastTemporalFeatureSplitService,
)
from alphainvest.modules.ai.application.price_forecast_temporal_ml_adapter import (
    PriceForecastTemporalMLAdapter,
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


def calculate_correlations(
    *,
    feature_names: tuple[str, ...],
    features: np.ndarray,
    targets: np.ndarray,
) -> list[tuple[str, float]]:
    correlations: list[
        tuple[str, float]
    ] = []

    for index, name in enumerate(
        feature_names
    ):
        feature = features[:, index]

        matrix = np.corrcoef(
            feature,
            targets,
        )

        correlation = float(
            matrix[0, 1]
        )

        correlations.append(
            (
                name,
                correlation,
            )
        )

    correlations.sort(
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    return correlations


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

        supervised = (
            PriceForecastTargetService
            .build_training_dataset(
                dataset=feature_dataset,
                horizon_sessions=(
                    configuration.horizon_sessions
                ),
            )
        )

        temporal_dataset = (
            PriceForecastTemporalFeatureService
            .build_dataset(
                dataset=supervised
            )
        )

        split = (
            PriceForecastTemporalFeatureSplitService
            .split(
                dataset=temporal_dataset,
                train_ratio=(
                    configuration.train_ratio
                ),
                validation_ratio=(
                    configuration.validation_ratio
                ),
            )
        )

        training = (
            PriceForecastTemporalMLAdapter
            .transform(
                split.train
            )
        )

        correlations = calculate_correlations(
            feature_names=training.feature_names,
            features=training.features,
            targets=training.targets,
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — SEÑAL TEMPORAL V3 "
            "PRONOSTICO_PRECIO"
        )
        print("=" * 72)

        print(f"Activo:             {asset.simbolo}")
        print(f"Fuente:             {SOURCE_NAME}")
        print(
            f"Feature rows:       "
            f"{feature_dataset.size}"
        )
        print(
            f"Targets originales: "
            f"{supervised.size}"
        )
        print(
            f"Temporal rows:      "
            f"{temporal_dataset.size}"
        )
        print(
            f"Lookback sessions:  "
            f"{temporal_dataset.lookback_sessions}"
        )
        print(
            f"Train rows:         "
            f"{training.rows}"
        )
        print(
            f"Validation rows:    "
            f"{split.validation_size}"
        )
        print(
            f"Test reservado:     "
            f"{split.test_size}"
        )
        print(
            f"Purge sessions:     "
            f"{split.purge_sessions}"
        )

        print()
        print(
            "CORRELACIÓN PEARSON "
            "FEATURE ↔ RETURN 5 SESIONES"
        )
        print("-" * 60)

        for name, correlation in correlations:
            print(
                f"{name:<24} "
                f"{correlation: .6f}"
            )

        print()
        print("=" * 72)
        print(
            "CÁLCULO REALIZADO EXCLUSIVAMENTE "
            "SOBRE TRAIN"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await analyze()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())