import asyncio
import hashlib
import json
import platform
from datetime import UTC, date, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

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

MODEL_CODE = "PRONOSTICO_PRECIO"
MODEL_VERSION = "0.1.0"

ALGORITHM = "HISTORICAL_MEDIAN_RETURN"
FRAMEWORK = "ALPHAINVEST_NATIVE"

START_DATE = date(2000, 1, 1)
END_DATE = date(2026, 8, 14)

ARTIFACT_DIRECTORY = (
    Path("artifacts")
    / "ai"
    / "pronostico_precio"
    / MODEL_VERSION
)

MODEL_PATH = (
    ARTIFACT_DIRECTORY
    / "model.json"
)

METADATA_PATH = (
    ARTIFACT_DIRECTORY
    / "metadata.json"
)


FINAL_TEST_METRICS = {
    "mae": 2.975142,
    "rmse": 3.886460,
    "r2": -0.008804,
    "direction_accuracy": 0.5508,
    "test_rows": 995,
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


def write_json(
    *,
    path: Path,
    content: dict[str, Any],
) -> None:
    path.write_text(
        json.dumps(
            content,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


async def build_artifact() -> None:
    experiment = PRICE_FORECAST_YAHOO_V1

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

        supervised_dataset = (
            PriceForecastTargetService
            .build_training_dataset(
                dataset=feature_dataset,
                horizon_sessions=(
                    experiment.horizon_sessions
                ),
            )
        )

        temporal_dataset = (
            PriceForecastTemporalFeatureService
            .build_dataset(
                dataset=supervised_dataset
            )
        )

        split = (
            PriceForecastTemporalFeatureSplitService
            .split(
                dataset=temporal_dataset,
                train_ratio=(
                    experiment.train_ratio
                ),
                validation_ratio=(
                    experiment.validation_ratio
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

        final_calibration_targets = np.concatenate(
            (
                training.targets,
                validation.targets,
            )
        )

        median_return_percentage = float(
            np.median(
                final_calibration_targets
            )
        )

        ARTIFACT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        created_at = datetime.now(UTC)

        model_content: dict[str, Any] = {
            "algorithm": ALGORITHM,
            "framework": FRAMEWORK,
            "model_code": MODEL_CODE,
            "model_version": MODEL_VERSION,
            "horizon_sessions": (
                experiment.horizon_sessions
            ),
            "target": (
                "future_return_percentage"
            ),
            "median_return_percentage": (
                median_return_percentage
            ),
            "calibration_rows": int(
                final_calibration_targets.size
            ),
            "source_name": SOURCE_NAME,
        }

        write_json(
            path=MODEL_PATH,
            content=model_content,
        )

        checksum = calculate_sha256(
            MODEL_PATH
        )

        metadata: dict[str, Any] = {
            "model": {
                "code": MODEL_CODE,
                "version": MODEL_VERSION,
                "algorithm": ALGORITHM,
                "framework": FRAMEWORK,
                "artifact_format": "JSON",
                "artifact_path": (
                    MODEL_PATH.as_posix()
                ),
                "sha256": checksum,
            },
            "experiment": {
                "symbol": SYMBOL,
                "asset_id": str(asset.id),
                "source_name": SOURCE_NAME,
                "start_date": (
                    START_DATE.isoformat()
                ),
                "end_date": (
                    END_DATE.isoformat()
                ),
                "horizon_sessions": (
                    experiment.horizon_sessions
                ),
                "target": (
                    "future_return_percentage"
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
                "selection_policy": (
                    "Menor MAE sobre VALIDATION; "
                    "RMSE y R² como métricas "
                    "secundarias."
                ),
            },
            "dataset": {
                "feature_rows": (
                    feature_dataset.size
                ),
                "targets": (
                    supervised_dataset.size
                ),
                "temporal_rows": (
                    temporal_dataset.size
                ),
                "train_rows": (
                    training.rows
                ),
                "validation_rows": (
                    validation.rows
                ),
                "final_calibration_rows": int(
                    final_calibration_targets.size
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
            "calibration": {
                "statistic": "MEDIAN",
                "median_return_percentage": (
                    median_return_percentage
                ),
                "calibration_scope": (
                    "TRAIN_PLUS_VALIDATION"
                ),
            },
            "selection": {
                "selected_algorithm": ALGORITHM,
                "selected_horizon_sessions": (
                    experiment.horizon_sessions
                ),
                "reason": (
                    "Los modelos Ridge, Huber y "
                    "XGBoost evaluados no superaron "
                    "consistentemente al baseline "
                    "TRAIN_MEDIAN sobre VALIDATION."
                ),
                "evaluated_feature_sets": [
                    "V1_RAW",
                    "V2_STATIONARY",
                    "V3_TEMPORAL",
                ],
                "evaluated_horizons_sessions": [
                    1,
                    5,
                    10,
                    20,
                ],
            },
            "features_used_during_selection": list(
                training.feature_names
            ),
            "runtime_requirement": {
                "requires_ml_model": False,
                "requires_feature_vector_at_inference": False,
                "requires_base_price": True,
            },
            "final_test_metrics": (
                FINAL_TEST_METRICS
            ),
            "runtime": {
                "python": (
                    platform.python_version()
                ),
                "numpy": version("numpy"),
            },
            "created_at": (
                created_at.isoformat()
            ),
            "status": "PROTOTYPE_EVALUATED",
            "limitations": [
                (
                    "Evaluado únicamente con histórico "
                    "de AAPL."
                ),
                (
                    "El estimador final utiliza la "
                    "mediana histórica del rendimiento "
                    "a cinco sesiones."
                ),
                (
                    "El R² final es ligeramente negativo "
                    "y no demuestra capacidad explicativa "
                    "superior a un estimador constante."
                ),
                (
                    "El resultado debe interpretarse "
                    "como estimación estadística educativa "
                    "y no como garantía de rendimiento."
                ),
                (
                    "El TEST final fue consumido una sola "
                    "vez y no debe reutilizarse para "
                    "selección o tuning."
                ),
            ],
        }

        write_json(
            path=METADATA_PATH,
            content=metadata,
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — ARTEFACTO "
            "PRONOSTICO_PRECIO"
        )
        print("=" * 72)

        print(
            f"Modelo:         {MODEL_CODE}"
        )

        print(
            f"Versión:        {MODEL_VERSION}"
        )

        print(
            f"Algoritmo:      {ALGORITHM}"
        )

        print(
            f"Artefacto:      {MODEL_PATH}"
        )

        print(
            f"Metadata:       {METADATA_PATH}"
        )

        print(
            f"SHA-256:        {checksum}"
        )

        print(
            "Median return:  "
            f"{median_return_percentage:.8f}%"
        )

        print(
            "Calibration:    "
            f"{final_calibration_targets.size}"
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