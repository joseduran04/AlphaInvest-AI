from decimal import Decimal

from alphainvest.modules.ai.application.temporal_split_service import (
    TrendTemporalSplitService,
)
from alphainvest.modules.ai.application.trend_target_service import (
    TrendTargetService,
)
from alphainvest.modules.ai.domain.feature_dataset import (
    AIFeatureDataset,
)
from alphainvest.modules.ai.domain.prediction_enums import (
    TrendClassification,
)
from alphainvest.modules.ai.domain.trend_analysis import (
    TrendClassDistribution,
    TrendExperimentAnalysis,
    TrendExperimentSpec,
)
from alphainvest.modules.ai.domain.trend_dataset import (
    TrendTrainingRow,
)


class TrendAnalysisService:
    """Analiza configuraciones candidatas de tendencia."""

    @staticmethod
    def analyze(
        *,
        feature_dataset: AIFeatureDataset,
        specification: TrendExperimentSpec,
        train_ratio: Decimal,
        validation_ratio: Decimal,
    ) -> TrendExperimentAnalysis:
        training_dataset = (
            TrendTargetService.build_training_dataset(
                dataset=feature_dataset,
                horizon_sessions=(
                    specification.horizon_sessions
                ),
                neutral_threshold_percentage=(
                    specification
                    .neutral_threshold_percentage
                ),
            )
        )

        split = TrendTemporalSplitService.split(
            dataset=training_dataset,
            train_ratio=train_ratio,
            validation_ratio=validation_ratio,
        )

        return TrendExperimentAnalysis(
            specification=specification,
            total_targets=training_dataset.size,
            total_purged=(
                split.purge_sessions * 2
            ),
            full_distribution=(
                TrendAnalysisService._distribution(
                    training_dataset.rows
                )
            ),
            train_distribution=(
                TrendAnalysisService._distribution(
                    split.train
                )
            ),
            validation_distribution=(
                TrendAnalysisService._distribution(
                    split.validation
                )
            ),
            test_distribution=(
                TrendAnalysisService._distribution(
                    split.test
                )
            ),
        )

    @staticmethod
    def analyze_many(
        *,
        feature_dataset: AIFeatureDataset,
        specifications: tuple[
            TrendExperimentSpec,
            ...,
        ],
        train_ratio: Decimal,
        validation_ratio: Decimal,
    ) -> tuple[TrendExperimentAnalysis, ...]:
        if not specifications:
            raise ValueError(
                "Debe proporcionarse al menos "
                "una configuración experimental"
            )

        return tuple(
            TrendAnalysisService.analyze(
                feature_dataset=feature_dataset,
                specification=specification,
                train_ratio=train_ratio,
                validation_ratio=validation_ratio,
            )
            for specification in specifications
        )

    @staticmethod
    def _distribution(
        rows: tuple[TrendTrainingRow, ...],
    ) -> TrendClassDistribution:
        bullish = 0
        neutral = 0
        bearish = 0

        for row in rows:
            classification = (
                row.target.classification
            )

            if (
                classification
                == TrendClassification.BULLISH
            ):
                bullish += 1

            elif (
                classification
                == TrendClassification.NEUTRAL
            ):
                neutral += 1

            else:
                bearish += 1

        return TrendClassDistribution(
            bullish=bullish,
            neutral=neutral,
            bearish=bearish,
            total=len(rows),
        )