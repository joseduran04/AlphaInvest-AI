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
from alphainvest.modules.ai.application.regression_evaluator import (
    RegressionEvaluator,
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


async def evaluate() -> None:
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
                train_ratio=configuration.train_ratio,
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

        validation = (
            PriceForecastTemporalMLAdapter
            .transform(
                split.validation
            )
        )

        test = (
            PriceForecastTemporalMLAdapter
            .transform(
                split.test
            )
        )

        final_training_targets = np.concatenate(
            (
                training.targets,
                validation.targets,
            )
        )

        final_median_return = float(
            np.median(
                final_training_targets
            )
        )

        predictions = np.full(
            test.targets.shape,
            final_median_return,
            dtype=np.float64,
        )

        metrics = RegressionEvaluator.evaluate(
            expected=test.targets,
            predicted=predictions,
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — EVALUACIÓN FINAL "
            "PRONOSTICO_PRECIO"
        )
        print("=" * 72)

        print(f"Activo:              {asset.simbolo}")
        print(f"Fuente:              {SOURCE_NAME}")

        print()
        print("Especificación")
        print(
            "Algoritmo:           "
            "HISTORICAL_MEDIAN_RETURN"
        )
        print(
            f"Horizonte:           "
            f"{configuration.horizon_sessions} sesiones"
        )
        print(
            "Target:              "
            "future_return_percentage"
        )

        print()
        print("Dataset")

        print(
            f"Feature rows:        "
            f"{feature_dataset.size}"
        )

        print(
            f"Targets:             "
            f"{supervised.size}"
        )

        print(
            f"Temporal rows:       "
            f"{temporal_dataset.size}"
        )

        print(
            f"Train:               "
            f"{training.rows}"
        )

        print(
            f"Validation:          "
            f"{validation.rows}"
        )

        print(
            f"Final calibration:   "
            f"{final_training_targets.size}"
        )

        print(
            f"TEST:                "
            f"{test.rows}"
        )

        print()
        print("Parámetro final")

        print(
            "Median return:       "
            f"{final_median_return:.8f}%"
        )

        print()
        print("TEST FINAL")

        print(
            f"MAE:                 "
            f"{metrics.mae:.6f}%"
        )

        print(
            f"RMSE:                "
            f"{metrics.rmse:.6f}%"
        )

        print(
            f"R²:                  "
            f"{metrics.r2:.6f}"
        )

        print(
            "Direction accuracy:  "
            f"{metrics.direction_accuracy:.4f}"
        )

        print()
        print("=" * 72)
        print(
            "TEST CONSUMIDO — NO UTILIZAR PARA "
            "SELECCIÓN NI NUEVO TUNING"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await evaluate()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())