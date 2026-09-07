import asyncio
import hashlib
import json
import platform
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from sklearn.utils.class_weight import (
    compute_sample_weight,
)
from xgboost import XGBClassifier

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

MODEL_CODE = "PREDICCION_TENDENCIA"
MODEL_VERSION = "0.1.0"

START_DATE = date(2000, 1, 1)
END_DATE = date(2026, 8, 14)

ARTIFACT_DIRECTORY = Path(
    "artifacts"
) / "ai" / "prediccion_tendencia" / MODEL_VERSION

MODEL_PATH = ARTIFACT_DIRECTORY / "model.ubj"
METADATA_PATH = ARTIFACT_DIRECTORY / "metadata.json"


FINAL_TEST_METRICS = {
    "accuracy": 0.3066,
    "balanced_accuracy": 0.3587,
    "macro_f1": 0.2573,
    "confusion_matrix": [
        [195, 43, 4],
        [314, 98, 12],
        [259, 60, 13],
    ],
    "test_rows": 998,
}


def calculate_sha256(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def build_classifier() -> XGBClassifier:
    configuration = PREDICTION_TREND_XGBOOST_V1

    return XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        n_estimators=configuration.n_estimators,
        max_depth=configuration.max_depth,
        learning_rate=configuration.learning_rate,
        min_child_weight=configuration.min_child_weight,
        subsample=configuration.subsample,
        colsample_bytree=configuration.colsample_bytree,
        reg_alpha=configuration.reg_alpha,
        reg_lambda=configuration.reg_lambda,
        eval_metric="mlogloss",
        random_state=configuration.random_state,
        n_jobs=1,
        tree_method="hist",
    )


def write_metadata(
    metadata: dict[str, Any],
) -> None:
    METADATA_PATH.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


async def build_artifact() -> None:
    experiment = PREDICTION_TREND_YAHOO_V1
    model_configuration = (
        PREDICTION_TREND_XGBOOST_V1
    )

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

        classifier = build_classifier()

        sample_weights = compute_sample_weight(
            class_weight="balanced",
            y=final_training.targets,
        )

        classifier.fit(
            final_training.features,
            final_training.targets,
            sample_weight=sample_weights,
        )

        ARTIFACT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        classifier.save_model(
            MODEL_PATH
        )

        checksum = calculate_sha256(
            MODEL_PATH
        )

        created_at = datetime.now(UTC)

        metadata: dict[str, Any] = {
            "model": {
                "code": MODEL_CODE,
                "version": MODEL_VERSION,
                "algorithm": "XGBoost",
                "framework": "xgboost",
                "artifact_format": "UBJSON",
                "artifact_path": MODEL_PATH.as_posix(),
                "sha256": checksum,
            },
            "experiment": {
                "symbol": SYMBOL,
                "asset_id": str(asset.id),
                "source_name": SOURCE_NAME,
                "start_date": START_DATE.isoformat(),
                "end_date": END_DATE.isoformat(),
                "horizon_sessions": (
                    experiment.horizon_sessions
                ),
                "neutral_threshold_percentage": str(
                    experiment
                    .neutral_threshold_percentage
                ),
                "train_ratio": str(
                    experiment.train_ratio
                ),
                "validation_ratio": str(
                    experiment.validation_ratio
                ),
                "test_ratio": str(
                    experiment.test_ratio
                ),
                "purge_sessions": (
                    split.purge_sessions
                ),
            },
            "dataset": {
                "feature_rows": (
                    feature_dataset.size
                ),
                "targets": (
                    supervised_dataset.size
                ),
                "final_training_rows": (
                    final_training.rows
                ),
                "test_rows": (
                    split.test_size
                ),
                "first_feature_date": (
                    feature_dataset
                    .start_date
                    .isoformat()
                ),
                "last_feature_date": (
                    feature_dataset
                    .end_date
                    .isoformat()
                ),
            },
            "features": list(
                final_training.feature_names
            ),
            "target_encoding": {
                "0": "BAJISTA",
                "1": "NEUTRAL",
                "2": "ALCISTA",
            },
            "hyperparameters": {
                "objective": "multi:softprob",
                "num_class": 3,
                "n_estimators": (
                    model_configuration.n_estimators
                ),
                "max_depth": (
                    model_configuration.max_depth
                ),
                "learning_rate": (
                    model_configuration.learning_rate
                ),
                "min_child_weight": (
                    model_configuration.min_child_weight
                ),
                "subsample": (
                    model_configuration.subsample
                ),
                "colsample_bytree": (
                    model_configuration.colsample_bytree
                ),
                "reg_alpha": (
                    model_configuration.reg_alpha
                ),
                "reg_lambda": (
                    model_configuration.reg_lambda
                ),
                "balanced_weights": (
                    model_configuration
                    .use_balanced_weights
                ),
                "random_state": (
                    model_configuration.random_state
                ),
            },
            "final_test_metrics": (
                FINAL_TEST_METRICS
            ),
            "runtime": {
                "python": platform.python_version(),
                "numpy": version("numpy"),
                "scikit_learn": version(
                    "scikit-learn"
                ),
                "xgboost": version("xgboost"),
            },
            "created_at": created_at.isoformat(),
            "status": "PROTOTYPE_EVALUATED",
            "limitations": [
                (
                    "Evaluado únicamente con histórico "
                    "de AAPL."
                ),
                (
                    "Las métricas finales no justifican "
                    "uso financiero productivo."
                ),
                (
                    "El TEST final fue consumido una sola "
                    "vez y no debe reutilizarse para tuning."
                ),
            ],
        }

        write_metadata(metadata)

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — ARTEFACTO "
            "PREDICCION_TENDENCIA"
        )
        print("=" * 72)

        print(
            f"Modelo:       {MODEL_CODE}"
        )
        print(
            f"Versión:      {MODEL_VERSION}"
        )
        print(
            f"Artefacto:    {MODEL_PATH}"
        )
        print(
            f"Metadata:     {METADATA_PATH}"
        )
        print(
            f"SHA-256:      {checksum}"
        )
        print(
            f"Training rows:{final_training.rows:>6}"
        )

        print()
        print(
            "Estado: PROTOTYPE_EVALUATED"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await build_artifact()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())