import asyncio
from datetime import date
from decimal import Decimal

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
    dispose_engine,
)
from alphainvest.modules.ai.application.feature_data_service import (
    AIFeatureDataService,
)
from alphainvest.modules.ai.application.trend_analysis_service import (
    TrendAnalysisService,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_analysis import (
    TrendClassDistribution,
    TrendExperimentAnalysis,
    TrendExperimentSpec,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)

SYMBOL = "AAPL"
SOURCE_NAME = "Yahoo Finance"

START_DATE = date(2000, 1, 1)
END_DATE = date.today()

TRAIN_RATIO = Decimal("0.70")
VALIDATION_RATIO = Decimal("0.15")

SPECIFICATIONS = (
    TrendExperimentSpec(
        horizon_sessions=1,
        neutral_threshold_percentage=Decimal("0.5"),
    ),
    TrendExperimentSpec(
        horizon_sessions=1,
        neutral_threshold_percentage=Decimal("1.0"),
    ),
    TrendExperimentSpec(
        horizon_sessions=5,
        neutral_threshold_percentage=Decimal("0.5"),
    ),
    TrendExperimentSpec(
        horizon_sessions=5,
        neutral_threshold_percentage=Decimal("1.0"),
    ),
    TrendExperimentSpec(
        horizon_sessions=5,
        neutral_threshold_percentage=Decimal("2.0"),
    ),
    TrendExperimentSpec(
        horizon_sessions=10,
        neutral_threshold_percentage=Decimal("1.0"),
    ),
    TrendExperimentSpec(
        horizon_sessions=10,
        neutral_threshold_percentage=Decimal("2.0"),
    ),
)


def format_percentage(
    distribution: TrendClassDistribution,
    classification: TrendClassification,
) -> str:
    percentage = distribution.percentage(
        classification
    )

    return f"{percentage:.2f}%"


def print_distribution(
    *,
    title: str,
    distribution: TrendClassDistribution,
) -> None:
    bullish = distribution.count(
        TrendClassification.BULLISH
    )
    neutral = distribution.count(
        TrendClassification.NEUTRAL
    )
    bearish = distribution.count(
        TrendClassification.BEARISH
    )

    bullish_percentage = format_percentage(
        distribution,
        TrendClassification.BULLISH,
    )
    neutral_percentage = format_percentage(
        distribution,
        TrendClassification.NEUTRAL,
    )
    bearish_percentage = format_percentage(
        distribution,
        TrendClassification.BEARISH,
    )

    print(f"  {title}")
    print(
        f"    ALCISTA : {bullish:>3} "
        f"({bullish_percentage})"
    )
    print(
        f"    NEUTRAL : {neutral:>3} "
        f"({neutral_percentage})"
    )
    print(
        f"    BAJISTA : {bearish:>3} "
        f"({bearish_percentage})"
    )
    print(
        f"    TOTAL   : {distribution.total:>3}"
    )


def print_analysis(
    analysis: TrendExperimentAnalysis,
) -> None:
    specification = analysis.specification

    print()
    print("=" * 72)
    print(
        "HORIZONTE: "
        f"{specification.horizon_sessions} sesiones"
    )
    print(
        "UMBRAL:    ±"
        f"{specification.neutral_threshold_percentage}%"
    )
    print(
        f"TARGETS:    {analysis.total_targets}"
    )
    print(
        f"PURGED:     {analysis.total_purged}"
    )
    print("-" * 72)

    print_distribution(
        title="GLOBAL",
        distribution=analysis.full_distribution,
    )

    print_distribution(
        title="TRAIN",
        distribution=analysis.train_distribution,
    )

    print_distribution(
        title="VALIDATION",
        distribution=(
            analysis.validation_distribution
        ),
    )

    print_distribution(
        title="TEST",
        distribution=analysis.test_distribution,
    )


async def run_analysis() -> None:
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

        dataset = await feature_service.build_dataset(
            asset_id=asset.id,
            start_date=START_DATE,
            end_date=END_DATE,
        )

        print()
        print("=" * 72)
        print("ALPHAINVEST AI — DIAGNÓSTICO DE TENDENCIA")
        print("=" * 72)
        print(f"Activo:        {asset.simbolo}")
        print(f"Asset ID:      {asset.id}")
        print(f"Fuente:        {SOURCE_NAME}")
        print(
            f"Feature rows:  {dataset.size}"
        )
        print(
            f"Primera fecha: {dataset.start_date}"
        )
        print(
            f"Última fecha:  {dataset.end_date}"
        )
        print(
            f"Train ratio:   {TRAIN_RATIO}"
        )
        print(
            f"Valid. ratio:  {VALIDATION_RATIO}"
        )
        print(
            "Test ratio:    "
            f"{Decimal('1') - TRAIN_RATIO - VALIDATION_RATIO}"
        )

        analyses = TrendAnalysisService.analyze_many(
            feature_dataset=dataset,
            specifications=SPECIFICATIONS,
            train_ratio=TRAIN_RATIO,
            validation_ratio=VALIDATION_RATIO,
        )

        for analysis in analyses:
            print_analysis(analysis)

        print()
        print("=" * 72)
        print("DIAGNÓSTICO FINALIZADO")
        print("=" * 72)


async def main() -> None:
    try:
        await run_analysis()
    finally:
        await dispose_engine()


if __name__ == "__main__":
    asyncio.run(main())