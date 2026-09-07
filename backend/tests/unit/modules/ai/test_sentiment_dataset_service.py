from decimal import Decimal

from bson.decimal128 import Decimal128

from alphainvest.modules.ai.application.sentiment_dataset_service import (
    SentimentDatasetService,
)
from alphainvest.modules.ai.domain.sentiment_enums import (
    SentimentClass,
)


def test_builds_sentiment_dataset(
) -> None:
    documents = [
        {
            "title": (
                "Company reports "
                "strong earnings"
            ),
            "summary": (
                "Revenue exceeded "
                "expectations."
            ),
            "provider_sentiment": {
                "score": Decimal128(
                    "0.45"
                ),
                "label": (
                    "Bullish"
                ),
            },
        },
        {
            "title": (
                "Shares fall after "
                "weak outlook"
            ),
            "summary": (
                "Management lowered "
                "guidance."
            ),
            "provider_sentiment": {
                "score": Decimal128(
                    "-0.40"
                ),
                "label": (
                    "Bearish"
                ),
            },
        },
        {
            "title": (
                "Company announces "
                "quarterly update"
            ),
            "summary": (
                "Results were broadly "
                "unchanged."
            ),
            "provider_sentiment": {
                "score": Decimal128(
                    "0.01"
                ),
                "label": (
                    "Neutral"
                ),
            },
        },
    ]

    dataset = (
        SentimentDatasetService
        .build(documents)
    )

    assert dataset.size == 3

    assert (
        dataset.samples[0].label
        == SentimentClass.POSITIVE
    )

    assert (
        dataset.samples[1].label
        == SentimentClass.NEGATIVE
    )

    assert (
        dataset.samples[2].label
        == SentimentClass.NEUTRAL
    )

    assert (
        dataset.samples[0]
        .provider_score
        == Decimal("0.45")
    )


def test_joins_title_and_summary(
) -> None:
    dataset = (
        SentimentDatasetService
        .build(
            [
                {
                    "title": "Apple rises",
                    "summary": (
                        "Demand remains strong"
                    ),
                    "provider_sentiment": {
                        "score": (
                            Decimal128(
                                "0.30"
                            )
                        ),
                        "label": "Bullish",
                    },
                }
            ]
        )
    )

    assert (
        dataset.samples[0].text
        == (
            "Apple rises "
            "Demand remains strong"
        )
    )


def test_skips_document_without_sentiment(
) -> None:
    dataset = (
        SentimentDatasetService
        .build(
            [
                {
                    "title": "Headline",
                    "summary": "Summary",
                }
            ]
        )
    )

    assert dataset.size == 0