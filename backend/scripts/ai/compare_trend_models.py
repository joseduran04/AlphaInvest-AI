import asyncio
from datetime import date

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.temporal_split_service import (
    TrendTemporalSplitService,
)
from alphainvest.modules.ai.application.trend_baseline_service import (
    TrendBaselineService,
)
from alphainvest.modules.ai.application.trend_ml_adapter import (
    TrendMLAdapter,
)
from alphainvest.modules.ai.application.trend_target_service import (
    TrendTargetService,
)
from alphainvest.modules.ai.application.trend_xgboost_service import (
    TrendXGBoostService,
)
from alphainvest.modules.ai.domain.ml_metrics import (
    ClassificationMetrics,
)
from alphainvest.modules.ai.domain.trend_experiment import (
    PREDICTION_TREND_YAHOO_V1,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

SYMBOL = "AAPL"
SOURCE_NAME = "Yahoo Finance"

START_DATE = date(2000, 1, 1)
END_DATE = date.today()


def print_metrics(
    *,
    name: str,
    metrics: ClassificationMetrics,
) -> None:
    print()
    print(name)
    print("-" * 60)
    print(
        f"Accuracy:          {metrics.accuracy:.4f}"
    )
    print(
        "Balanced accuracy: "
        f"{metrics.balanced_accuracy:.4f}"
    )
    print(
        f"Macro F1:          {metrics.macro_f1:.4f}"
    )

    print()
    print("Confusion matrix")
    print("             PRED")
    print("          B      N      A")

    labels = (
        "B",
        "N",
        "A",
    )

    for label, row in zip(
        labels,
        metrics.confusion_matrix,
        strict=True,
    ):
        print(
            f"REAL {label} "
            f"{row[0]:>6} "
            f"{row[1]:>6} "
            f"{row[2]:>6}"
        )


async def compare_models() -> None:
    configuration = PREDICTION_TREND_YAHOO_V1

    async with AsyncSessionFactory() as session:
        repository = MarketRepository(session)

        asset = (
            await repository.get_active_asset_by_symbol(
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

        features = await feature_service.build_dataset(
            asset_id=asset.id,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        supervised = (
            TrendTargetService.build_training_dataset(
                dataset=features,
                horizon_sessions=(
                    configuration.horizon_sessions
                ),
                neutral_threshold_percentage=(
                    configuration
                    .neutral_threshold_percentage
                ),
            )
        )

        split = TrendTemporalSplitService.split(
            dataset=supervised,
            train_ratio=configuration.train_ratio,
            validation_ratio=(
                configuration.validation_ratio
            ),
        )

        training = TrendMLAdapter.transform(
            split.train
        )

        validation = TrendMLAdapter.transform(
            split.validation
        )

        _, baseline_result = (
            TrendBaselineService.train_and_evaluate(
                training=training,
                validation=validation,
            )
        )

        _, xgboost_result = (
            TrendXGBoostService.train_and_evaluate(
                training=training,
                validation=validation,
            )
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — COMPARACIÓN "
            "PREDICCION_TENDENCIA"
        )
        print("=" * 72)

        print(f"Activo:          {asset.simbolo}")
        print(f"Feature rows:    {features.size}")
        print(f"Targets:         {supervised.size}")
        print(f"Train:           {split.train_size}")
        print(
            f"Validation:      "
            f"{split.validation_size}"
        )
        print(
            f"Test reservado:  {split.test_size}"
        )

        print_metrics(
            name="LOGISTIC REGRESSION",
            metrics=baseline_result.metrics,
        )

        print_metrics(
            name="XGBOOST",
            metrics=xgboost_result.metrics,
        )

        print()
        print("=" * 72)
        print(
            "TEST NO UTILIZADO — "
            "selección basada únicamente en VALIDATION"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await compare_models()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())