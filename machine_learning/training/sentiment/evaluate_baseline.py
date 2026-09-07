from __future__ import annotations

import csv
import sys
from pathlib import Path


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

PROJECT_ROOT = (
    ROOT_DIR.parent
)

BACKEND_SRC = (
    PROJECT_ROOT
    / "backend"
    / "src"
)

sys.path.insert(
    0,
    str(BACKEND_SRC),
)

from alphainvest.modules.ai.application.sentiment_baseline_service import (  # noqa: E402
    SentimentBaselineService,
)


DATASET_DIR = (
    ROOT_DIR
    / "datasets"
    / "sentiment"
    / "financial_phrasebank"
    / "processed"
)

TRAIN_FILE = (
    DATASET_DIR
    / "train.csv"
)

VALIDATION_FILE = (
    DATASET_DIR
    / "validation.csv"
)


def read_dataset(
    path: Path,
) -> tuple[
    list[str],
    list[str],
]:
    texts: list[str] = []
    labels: list[str] = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(
            file
        )

        for row in reader:
            texts.append(
                row["text"]
            )

            labels.append(
                row["label"]
            )

    return (
        texts,
        labels,
    )


def main() -> None:
    train_texts, train_labels = (
        read_dataset(
            TRAIN_FILE
        )
    )

    validation_texts, validation_labels = (
        read_dataset(
            VALIDATION_FILE
        )
    )

    _, result = (
        SentimentBaselineService
        .train_and_evaluate(
            train_texts=train_texts,
            train_labels=train_labels,
            evaluation_texts=(
                validation_texts
            ),
            evaluation_labels=(
                validation_labels
            ),
        )
    )

    print(
        "=" * 72
    )

    print(
        "ALPHAINVEST AI — "
        "SENTIMENT BASELINE"
    )

    print(
        "=" * 72
    )

    print(
        "Train:",
        len(train_texts),
    )

    print(
        "Validation:",
        len(validation_texts),
    )

    print()

    print(
        f"Accuracy:          "
        f"{result.accuracy:.4f}"
    )

    print(
        f"Balanced accuracy: "
        f"{result.balanced_accuracy:.4f}"
    )

    print(
        f"Macro F1:          "
        f"{result.macro_f1:.4f}"
    )

    print()

    print(
        "Labels:",
        result.labels,
    )

    print()

    print(
        "Confusion matrix:"
    )

    for label, row in zip(
        result.labels,
        result.confusion_matrix,
        strict=True,
    ):
        print(
            f"{label:<10}",
            row,
        )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()