from __future__ import annotations

import csv
from pathlib import Path
from statistics import mean

from transformers import AutoTokenizer

MODEL_ID = "yiyanghkust/finbert-pretrain"

MODEL_REVISION = (
    "88ab954a39ea6d3ce2b62cff086dd5ad1172c664"
)


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

DATASET_DIR = (
    ROOT_DIR
    / "datasets"
    / "sentiment"
    / "financial_phrasebank"
    / "processed"
)

CACHE_DIR = (
    ROOT_DIR
    / "saved_models"
    / "huggingface"
)

TRAIN_FILE = DATASET_DIR / "train.csv"

VALIDATION_FILE = (
    DATASET_DIR
    / "validation.csv"
)


def read_texts(
    path: Path,
) -> list[str]:
    texts: list[str] = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            texts.append(
                row["text"]
            )

    return texts


def percentile(
    values: list[int],
    fraction: float,
) -> int:
    ordered = sorted(values)

    index = round(
        (len(ordered) - 1)
        * fraction
    )

    return ordered[index]


def main() -> None:
    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=CACHE_DIR,
        )
    )

    train_texts = read_texts(
        TRAIN_FILE
    )

    validation_texts = read_texts(
        VALIDATION_FILE
    )

    texts = (
        train_texts
        + validation_texts
    )

    lengths = [
        len(
            tokenizer(
                text,
                add_special_tokens=True,
                truncation=False,
            )["input_ids"]
        )
        for text in texts
    ]

    print("=" * 72)

    print(
        "ALPHAINVEST AI — "
        "FINBERT TOKEN LENGTHS"
    )

    print("=" * 72)

    print(
        "Train:",
        len(train_texts),
    )

    print(
        "Validation:",
        len(validation_texts),
    )

    print(
        "Analyzed:",
        len(lengths),
    )

    print()

    print(
        "Mean:",
        f"{mean(lengths):.2f}",
    )

    print(
        "P50:",
        percentile(
            lengths,
            0.50,
        ),
    )

    print(
        "P90:",
        percentile(
            lengths,
            0.90,
        ),
    )

    print(
        "P95:",
        percentile(
            lengths,
            0.95,
        ),
    )

    print(
        "P99:",
        percentile(
            lengths,
            0.99,
        ),
    )

    print(
        "Max:",
        max(lengths),
    )

    for limit in (
        64,
        96,
        128,
        256,
        512,
    ):
        over_limit = sum(
            length > limit
            for length in lengths
        )

        percentage = (
            over_limit
            / len(lengths)
            * 100
        )

        print(
            f"> {limit:<3}: "
            f"{over_limit:>4} "
            f"({percentage:6.2f}%)"
        )

    print("=" * 72)


if __name__ == "__main__":
    main()