import asyncio
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

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
from alphainvest.modules.ai.application.price_forecast_horizon_comparison import (
    calculate_improvement,
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
from alphainvest.modules.ai.application.price_forecast_xgboost_service import (
    PriceForecastXGBoostService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

SYMBOL = "AAPL"
SOURCE_NAME = "Yahoo Finance"

START_DATE = date(2000, 1, 1)
END_DATE = date(2026, 8, 14)

TRAIN_RATIO = Decimal("0.70")
VALIDATION_RATIO = Decimal("0.15")

HORIZONS = (
    1,
    5,
    10,
    20,
)


@dataclass(frozen=True, slots=True)
class HorizonComparison:
    horizon_sessions: int

    target_rows: int
    temporal_rows: int

    train_rows: int
    validation_rows: int
    test_rows: int

    baseline_mae: float
    baseline_rmse: float
    baseline_r2: float
    baseline_direction_accuracy: float

    xgboost_mae: float
    xgboost_rmse: float
    xgboost_r2: float
    xgboost_direction_accuracy: float

    mae_improvement_percentage: float
    rmse_improvement_percentage: float



async def compare_horizon(
    *,
    feature_dataset: AIFeatureDataset,
    horizon_sessions: int,
) -> HorizonComparison:
    supervised = (
        PriceForecastTargetService
        .build_training_dataset(
            dataset=feature_dataset,
            horizon_sessions=horizon_sessions,
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
            train_ratio=TRAIN_RATIO,
            validation_ratio=VALIDATION_RATIO,
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

    baseline = (
        PriceForecastBaselineService
        .evaluate_train_median(
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

    return HorizonComparison(
        horizon_sessions=horizon_sessions,
        target_rows=supervised.size,
        temporal_rows=temporal_dataset.size,
        train_rows=training.rows,
        validation_rows=validation.rows,
        test_rows=split.test_size,
        baseline_mae=baseline.metrics.mae,
        baseline_rmse=baseline.metrics.rmse,
        baseline_r2=baseline.metrics.r2,
        baseline_direction_accuracy=(
            baseline.metrics.direction_accuracy
        ),
        xgboost_mae=xgboost.metrics.mae,
        xgboost_rmse=xgboost.metrics.rmse,
        xgboost_r2=xgboost.metrics.r2,
        xgboost_direction_accuracy=(
            xgboost.metrics.direction_accuracy
        ),
        mae_improvement_percentage=(
            calculate_improvement(
                baseline=baseline.metrics.mae,
                candidate=xgboost.metrics.mae,
            )
        ),
        rmse_improvement_percentage=(
            calculate_improvement(
                baseline=baseline.metrics.rmse,
                candidate=xgboost.metrics.rmse,
            )
        ),
    )


def print_result(
    result: HorizonComparison,
) -> None:
    print()
    print("=" * 72)
    print(
        f"HORIZONTE: "
        f"{result.horizon_sessions} sesiones"
    )
    print("=" * 72)

    print(
        f"Targets:          {result.target_rows}"
    )
    print(
        f"Temporal rows:    {result.temporal_rows}"
    )
    print(
        f"Train:            {result.train_rows}"
    )
    print(
        f"Validation:       {result.validation_rows}"
    )
    print(
        f"Test reservado:   {result.test_rows}"
    )

    print()
    print("TRAIN_MEDIAN")
    print("-" * 60)

    print(
        f"MAE:                "
        f"{result.baseline_mae:.6f}%"
    )

    print(
        f"RMSE:               "
        f"{result.baseline_rmse:.6f}%"
    )

    print(
        f"R²:                 "
        f"{result.baseline_r2:.6f}"
    )

    print(
        "Direction accuracy: "
        f"{result.baseline_direction_accuracy:.4f}"
    )

    print()
    print("XGBOOST_REGRESSOR")
    print("-" * 60)

    print(
        f"MAE:                "
        f"{result.xgboost_mae:.6f}%"
    )

    print(
        f"RMSE:               "
        f"{result.xgboost_rmse:.6f}%"
    )

    print(
        f"R²:                 "
        f"{result.xgboost_r2:.6f}"
    )

    print(
        "Direction accuracy: "
        f"{result.xgboost_direction_accuracy:.4f}"
    )

    print()
    print("MEJORA XGBOOST VS MEDIANA")
    print("-" * 60)

    print(
        f"MAE improvement:    "
        f"{result.mae_improvement_percentage:+.4f}%"
    )

    print(
        f"RMSE improvement:   "
        f"{result.rmse_improvement_percentage:+.4f}%"
    )


def print_summary(
    results: list[HorizonComparison],
) -> None:
    print()
    print("#" * 88)
    print(
        "RESUMEN — HORIZONTES "
        "PRONOSTICO_PRECIO"
    )
    print("#" * 88)

    print(
        f"{'H':>3} "
        f"{'MED_MAE':>10} "
        f"{'XGB_MAE':>10} "
        f"{'ΔMAE%':>9} "
        f"{'MED_RMSE':>10} "
        f"{'XGB_RMSE':>10} "
        f"{'ΔRMSE%':>9} "
        f"{'XGB_R2':>10} "
        f"{'DIR':>8}"
    )

    print("-" * 88)

    for result in results:
        print(
            f"{result.horizon_sessions:>3} "
            f"{result.baseline_mae:>10.4f} "
            f"{result.xgboost_mae:>10.4f} "
            f"{result.mae_improvement_percentage:>+9.2f} "
            f"{result.baseline_rmse:>10.4f} "
            f"{result.xgboost_rmse:>10.4f} "
            f"{result.rmse_improvement_percentage:>+9.2f} "
            f"{result.xgboost_r2:>10.4f} "
            f"{result.xgboost_direction_accuracy:>8.4f}"
        )

    print()
    print(
        "Δ positivo = XGBoost mejora "
        "respecto a TRAIN_MEDIAN."
    )

    print(
        "Δ negativo = XGBoost empeora "
        "respecto a TRAIN_MEDIAN."
    )

    print()
    print(
        "TEST NO UTILIZADO PARA EVALUACIÓN "
        "PREDICTIVA NI SELECCIÓN"
    )

    print("#" * 88)


async def compare() -> None:
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

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — COMPARACIÓN "
            "DE HORIZONTES PRONOSTICO_PRECIO"
        )
        print("=" * 72)

        print(f"Activo:       {asset.simbolo}")
        print(f"Fuente:       {SOURCE_NAME}")
        print(
            f"Feature rows: "
            f"{feature_dataset.size}"
        )

        results: list[
            HorizonComparison
        ] = []

        for horizon in HORIZONS:
            result = await compare_horizon(
                feature_dataset=feature_dataset,
                horizon_sessions=horizon,
            )

            results.append(result)

            print_result(result)

        print_summary(results)


async def main() -> None:
    try:
        await compare()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())