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


def print_confusion_matrix(
    matrix: tuple[
        tuple[int, ...],
        ...,
    ],
) -> None:
    print()
    print("Matriz de confusión")
    print("Filas = real")
    print("Columnas = predicción")
    print()
    print("          BAJISTA  NEUTRAL  ALCISTA")

    labels = (
        "BAJISTA",
        "NEUTRAL",
        "ALCISTA",
    )

    for label, row in zip(
        labels,
        matrix,
        strict=True,
    ):
        print(
            f"{label:<8} "
            f"{row[0]:>8} "
            f"{row[1]:>8} "
            f"{row[2]:>8}"
        )


async def run_training() -> None:
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

        training_dataset = (
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

        temporal_split = (
            TrendTemporalSplitService.split(
                dataset=training_dataset,
                train_ratio=(
                    configuration.train_ratio
                ),
                validation_ratio=(
                    configuration.validation_ratio
                ),
            )
        )

        training_ml = TrendMLAdapter.transform(
            temporal_split.train
        )

        validation_ml = TrendMLAdapter.transform(
            temporal_split.validation
        )

        _, result = (
            TrendBaselineService
            .train_and_evaluate(
                training=training_ml,
                validation=validation_ml,
            )
        )

        print()
        print("=" * 72)
        print(
            "ALPHAINVEST AI — BASELINE "
            "PREDICCION_TENDENCIA"
        )
        print("=" * 72)

        print(f"Activo:              {asset.simbolo}")
        print(f"Asset ID:            {asset.id}")
        print(f"Fuente:              {SOURCE_NAME}")

        print()
        print("Configuración experimental")
        print(
            "Horizonte:           "
            f"{configuration.horizon_sessions} sesión"
        )
        print(
            "Umbral neutral:      ±"
            f"{configuration.neutral_threshold_percentage}%"
        )
        print(
            "Train ratio:         "
            f"{configuration.train_ratio}"
        )
        print(
            "Validation ratio:    "
            f"{configuration.validation_ratio}"
        )
        print(
            "Test ratio:          "
            f"{configuration.test_ratio}"
        )

        print()
        print("Dataset")
        print(
            f"Feature rows:        "
            f"{feature_dataset.size}"
        )
        print(
            f"Targets:             "
            f"{training_dataset.size}"
        )
        print(
            f"Train rows:          "
            f"{temporal_split.train_size}"
        )
        print(
            f"Validation rows:     "
            f"{temporal_split.validation_size}"
        )
        print(
            f"Test rows reservadas:"
            f" {temporal_split.test_size}"
        )
        print(
            f"Purge sessions:      "
            f"{temporal_split.purge_sessions}"
        )

        print()
        print("Modelo")
        print(
            f"Algoritmo:           "
            f"{result.algorithm}"
        )

        print()
        print("VALIDATION")
        print(
            f"Accuracy:            "
            f"{result.metrics.accuracy:.4f}"
        )
        print(
            f"Balanced accuracy:   "
            f"{result.metrics.balanced_accuracy:.4f}"
        )
        print(
            f"Macro F1:            "
            f"{result.metrics.macro_f1:.4f}"
        )

        print_confusion_matrix(
            result.metrics.confusion_matrix
        )

        print()
        print("=" * 72)
        print(
            "TEST NO UTILIZADO — "
            "reservado para evaluación final"
        )
        print("=" * 72)


async def main() -> None:
    try:
        await run_training()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())