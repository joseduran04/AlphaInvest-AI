import asyncio
from datetime import date

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.price_forecast_baseline_service import (
    PriceForecastBaselineService,
)
from alphainvest.modules.ai.application.price_forecast_linear_service import (
    PriceForecastLinearService,
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
from alphainvest.modules.ai.application.price_forecast_xgboost_service import (
    PriceForecastXGBoostService,
)
from alphainvest.modules.ai.domain.ml_metrics import (
    RegressionMetrics,
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


def print_metrics(
    metrics: RegressionMetrics,
) -> None:
    print(
        f"MAE:                "
        f"{metrics.mae:.6f}%"
    )

    print(
        f"RMSE:               "
        f"{metrics.rmse:.6f}%"
    )

    print(
        f"R²:                 "
        f"{metrics.r2:.6f}"
    )

    print(
        "Direction accuracy: "
        f"{metrics.direction_accuracy:.4f}"
    )


async def compare() -> None:
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

        training = PriceForecastMLAdapter.transform(
            split.train
        )

        validation = (
            PriceForecastMLAdapter.transform(
                split.validation
            )
        )

        zero = (
            PriceForecastBaselineService
            .evaluate_zero(
                training=training,
                validation=validation,
            )
        )

        mean = (
            PriceForecastBaselineService
            .evaluate_train_mean(
                training=training,
                validation=validation,
            )
        )

        median = (
            PriceForecastBaselineService
            .evaluate_train_median(
                training=training,
                validation=validation,
            )
        )

        _, ridge = (
            PriceForecastLinearService
            .train_and_evaluate_ridge(
                training=training,
                validation=validation,
            )
        )

        _, huber = (
            PriceForecastLinearService
            .train_and_evaluate_huber(
                training=training,
                validation=validation,
            )
        )

        _, xgboost = (
            PriceForecastXGBoostService
            .train_and_evaluate(
                training=training,
                validation=validation,
            )
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — COMPARACIÓN "
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
            f"Train:           {training.rows}"
        )
        print(
            f"Validation:      "
            f"{validation.rows}"
        )
        print(
            f"Test reservado:  "
            f"{split.test_size}"
        )

        for result in (
            zero,
            mean,
            median,
        ):
            print()
            print(result.algorithm)
            print("-" * 60)
            print(
                "Predicción constante: "
                f"{result.constant_prediction:.6f}%"
            )
            print_metrics(
                result.metrics
            )

        for regression_result in (
            ridge,
            huber,
        ):
            print()
            print(regression_result.algorithm)
            print("-" * 60)

            print_metrics(
                regression_result.metrics
            )

        print()
        print("XGBOOST_REGRESSOR")
        print("-" * 60)

        print_metrics(
            xgboost.metrics
        )

        print()
        print("=" * 72)
        print(
            "TEST NO UTILIZADO — "
            "comparación únicamente sobre VALIDATION"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await compare()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())