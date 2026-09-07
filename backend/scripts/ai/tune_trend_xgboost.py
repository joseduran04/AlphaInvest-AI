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
from alphainvest.modules.ai.application.trend_ml_adapter import (
    TrendMLAdapter,
)
from alphainvest.modules.ai.application.trend_target_service import (
    TrendTargetService,
)
from alphainvest.modules.ai.application.trend_xgboost_tuning_service import (
    TrendXGBoostTuningService,
)
from alphainvest.modules.ai.domain.ml_metrics import (
    ClassificationMetrics,
)
from alphainvest.modules.ai.domain.trend_experiment import (
    PREDICTION_TREND_YAHOO_V1,
)
from alphainvest.modules.ai.domain.xgboost_tuning import (
    XGBoostCandidateResult,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

SYMBOL = "AAPL"
SOURCE_NAME = "Yahoo Finance"

START_DATE = date(2000, 1, 1)
END_DATE = date.today()


def print_confusion_matrix(
    metrics: ClassificationMetrics,
) -> None:
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


def print_candidate(
    result: XGBoostCandidateResult,
) -> None:
    candidate = result.candidate
    metrics = result.metrics

    print()
    print("=" * 72)
    print(candidate.name)
    print("=" * 72)

    print(
        "Balanced weights: "
        f"{candidate.use_balanced_weights}"
    )
    print(
        f"n_estimators:     "
        f"{candidate.n_estimators}"
    )
    print(
        f"max_depth:        "
        f"{candidate.max_depth}"
    )
    print(
        f"learning_rate:    "
        f"{candidate.learning_rate}"
    )
    print(
        f"min_child_weight: "
        f"{candidate.min_child_weight}"
    )
    print(
        f"subsample:        "
        f"{candidate.subsample}"
    )
    print(
        f"colsample_bytree: "
        f"{candidate.colsample_bytree}"
    )
    print(
        f"reg_alpha:        "
        f"{candidate.reg_alpha}"
    )
    print(
        f"reg_lambda:       "
        f"{candidate.reg_lambda}"
    )

    print()
    print("VALIDATION")
    print(
        f"Accuracy:          "
        f"{metrics.accuracy:.4f}"
    )
    print(
        f"Balanced accuracy: "
        f"{metrics.balanced_accuracy:.4f}"
    )
    print(
        f"Macro F1:          "
        f"{metrics.macro_f1:.4f}"
    )

    predicted_classes = sorted(
        set(result.predicted_classes)
    )

    print(
        "Clases predichas:  "
        f"{predicted_classes}"
    )

    print()
    print_confusion_matrix(metrics)


async def run_tuning() -> None:
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
                f"No existe un activo ACTIVO "
                f"con símbolo {SYMBOL}"
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

        supervised_dataset = (
            TrendTargetService.build_training_dataset(
                dataset=feature_dataset,
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
            dataset=supervised_dataset,
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

        result = TrendXGBoostTuningService.tune(
            training=training,
            validation=validation,
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — TUNING XGBOOST "
            "PREDICCION_TENDENCIA"
        )
        print("=" * 72)

        print(f"Activo:             {asset.simbolo}")
        print(
            f"Feature rows:       "
            f"{feature_dataset.size}"
        )
        print(
            f"Targets:            "
            f"{supervised_dataset.size}"
        )
        print(
            f"Train:              "
            f"{split.train_size}"
        )
        print(
            f"Validation:         "
            f"{split.validation_size}"
        )
        print(
            f"Test reservado:     "
            f"{split.test_size}"
        )

        print()
        print(
            "TEST NO UTILIZADO DURANTE EL TUNING"
        )

        for candidate_result in result.candidates:
            print_candidate(candidate_result)

        print()
        print("#" * 72)
        print("MEJOR CANDIDATO SOBRE VALIDATION")
        print("#" * 72)

        print_candidate(result.best)

        print()
        print(
            "Criterio:"
        )
        print(
            "1. Macro F1"
        )
        print(
            "2. Balanced Accuracy"
        )
        print(
            "3. Número de clases predichas"
        )
        print(
            "4. Accuracy"
        )

        print()
        print("=" * 72)
        print(
            "TEST SIGUE RESERVADO PARA "
            "LA EVALUACIÓN FINAL"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await run_tuning()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())