import asyncio
from datetime import date

import numpy as np
from sklearn.utils.class_weight import (
    compute_sample_weight,
)
from xgboost import XGBClassifier

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.classification_evaluator import (
    ClassificationEvaluator,
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
from alphainvest.modules.ai.domain.ml_metrics import (
    ClassificationMetrics,
)
from alphainvest.modules.ai.domain.trend_experiment import (
    PREDICTION_TREND_YAHOO_V1,
)
from alphainvest.modules.ai.domain.trend_model_spec import (
    PREDICTION_TREND_XGBOOST_V1,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

SYMBOL = "AAPL"
SOURCE_NAME = "Yahoo Finance"

START_DATE = date(2000, 1, 1)
END_DATE = date.today()


def print_metrics(
    metrics: ClassificationMetrics,
) -> None:
    print(f"Accuracy:          {metrics.accuracy:.4f}")
    print(
        "Balanced accuracy: "
        f"{metrics.balanced_accuracy:.4f}"
    )
    print(f"Macro F1:          {metrics.macro_f1:.4f}")

    print()
    print("Confusion matrix")
    print("             PRED")
    print("          B      N      A")

    labels = ("B", "N", "A")

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


async def evaluate_final_model() -> None:
    experiment = PREDICTION_TREND_YAHOO_V1
    model_config = PREDICTION_TREND_XGBOOST_V1

    async with AsyncSessionFactory() as session:
        repository = MarketRepository(session)

        asset = await repository.get_active_asset_by_symbol(
            SYMBOL
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

        supervised_dataset = (
            TrendTargetService.build_training_dataset(
                dataset=feature_dataset,
                horizon_sessions=(
                    experiment.horizon_sessions
                ),
                neutral_threshold_percentage=(
                    experiment
                    .neutral_threshold_percentage
                ),
            )
        )

        split = TrendTemporalSplitService.split(
            dataset=supervised_dataset,
            train_ratio=experiment.train_ratio,
            validation_ratio=(
                experiment.validation_ratio
            ),
        )

        final_training_rows = (
            split.train
            + split.validation
        )

        final_training = TrendMLAdapter.transform(
            final_training_rows
        )

        test = TrendMLAdapter.transform(
            split.test
        )

        classifier = XGBClassifier(
            objective="multi:softprob",
            num_class=3,
            n_estimators=model_config.n_estimators,
            max_depth=model_config.max_depth,
            learning_rate=model_config.learning_rate,
            min_child_weight=(
                model_config.min_child_weight
            ),
            subsample=model_config.subsample,
            colsample_bytree=(
                model_config.colsample_bytree
            ),
            reg_alpha=model_config.reg_alpha,
            reg_lambda=model_config.reg_lambda,
            eval_metric="mlogloss",
            random_state=model_config.random_state,
            n_jobs=1,
            tree_method="hist",
        )

        sample_weights = compute_sample_weight(
            class_weight="balanced",
            y=final_training.targets,
        )

        classifier.fit(
            final_training.features,
            final_training.targets,
            sample_weight=sample_weights,
        )

        prediction_values = classifier.predict(
            test.features
        )

        predictions = np.asarray(
            prediction_values,
            dtype=np.int64,
        )

        metrics = ClassificationEvaluator.evaluate(
            expected=test.targets,
            predicted=predictions,
        )

        probabilities = classifier.predict_proba(
            test.features
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — EVALUACIÓN FINAL "
            "PREDICCION_TENDENCIA"
        )
        print("=" * 72)

        print(f"Activo:              {asset.simbolo}")
        print(f"Fuente:              {SOURCE_NAME}")

        print()
        print("Especificación")
        print(
            "Horizonte:           "
            f"{experiment.horizon_sessions} sesiones"
        )
        print(
            "Umbral neutral:      ±"
            f"{experiment.neutral_threshold_percentage}%"
        )
        print("Algoritmo:           XGBOOST")
        print("Configuración:       BASE_WEIGHTED")

        print()
        print("Dataset")
        print(
            f"Feature rows:        "
            f"{feature_dataset.size}"
        )
        print(
            f"Targets:             "
            f"{supervised_dataset.size}"
        )
        print(
            f"Final training:      "
            f"{final_training.rows}"
        )
        print(
            f"TEST:                "
            f"{test.rows}"
        )

        print()
        print("TEST FINAL")
        print_metrics(metrics)

        print()
        print(
            "Probability rows:    "
            f"{probabilities.shape[0]}"
        )
        print(
            "Probability classes: "
            f"{probabilities.shape[1]}"
        )

        print()
        print("=" * 72)
        print(
            "TEST CONSUMIDO — NO UTILIZAR PARA "
            "NUEVO TUNING"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await evaluate_final_model()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())