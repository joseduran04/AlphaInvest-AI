from alphainvest.modules.ai.application.sentiment_baseline_service import (
    SENTIMENT_LABELS,
    SentimentBaselineService,
)


def test_builds_sentiment_pipeline() -> None:
    pipeline = (
        SentimentBaselineService
        .build_pipeline()
    )

    assert "tfidf" in pipeline.named_steps

    assert (
        "classifier"
        in pipeline.named_steps
    )


def test_trains_and_evaluates_sentiment_baseline(
) -> None:
    train_texts = [
        "profits increased strongly",
        "revenue growth exceeded expectations",
        "shares rose after strong earnings",
        "company reported heavy losses",
        "sales declined sharply",
        "guidance was reduced",
        "company released quarterly results",
        "meeting will be held tomorrow",
        "board approved the annual report",
    ]

    train_labels = [
        "POSITIVO",
        "POSITIVO",
        "POSITIVO",
        "NEGATIVO",
        "NEGATIVO",
        "NEGATIVO",
        "NEUTRAL",
        "NEUTRAL",
        "NEUTRAL",
    ]

    evaluation_texts = [
        "earnings growth was strong",
        "company reported declining sales",
        "annual report was published",
    ]

    evaluation_labels = [
        "POSITIVO",
        "NEGATIVO",
        "NEUTRAL",
    ]

    pipeline, result = (
        SentimentBaselineService
        .train_and_evaluate(
            train_texts=train_texts,
            train_labels=train_labels,
            evaluation_texts=(
                evaluation_texts
            ),
            evaluation_labels=(
                evaluation_labels
            ),
        )
    )

    assert pipeline is not None

    assert (
        result.labels
        == SENTIMENT_LABELS
    )

    assert (
        0.0
        <= result.accuracy
        <= 1.0
    )

    assert (
        0.0
        <= result.balanced_accuracy
        <= 1.0
    )

    assert (
        0.0
        <= result.macro_f1
        <= 1.0
    )

    assert (
        len(
            result.confusion_matrix
        )
        == 3
    )