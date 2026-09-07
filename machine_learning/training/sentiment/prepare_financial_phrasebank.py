from __future__ import annotations

import csv
import random
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


RANDOM_SEED = 42

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15

SOURCE_ENCODING = "latin-1"

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
)

SOURCE_FILE = (
    DATASET_DIR
    / "FinancialPhraseBank-v1.0"
    / "Sentences_50Agree.txt"
)

OUTPUT_DIR = (
    DATASET_DIR
    / "processed"
)

NORMALIZED_FILE = (
    OUTPUT_DIR
    / "financial_phrasebank_50agree.csv"
)

TRAIN_FILE = (
    OUTPUT_DIR
    / "train.csv"
)

VALIDATION_FILE = (
    OUTPUT_DIR
    / "validation.csv"
)

TEST_FILE = (
    OUTPUT_DIR
    / "test.csv"
)


LABEL_MAP = {
    "positive": "POSITIVO",
    "neutral": "NEUTRAL",
    "negative": "NEGATIVO",
}


@dataclass(frozen=True, slots=True)
class Sample:
    text: str
    label: str


def read_samples() -> list[Sample]:
    if not SOURCE_FILE.is_file():
        raise FileNotFoundError(
            "No existe el archivo fuente: "
            f"{SOURCE_FILE}"
        )

    samples: list[Sample] = []

    seen: set[
        tuple[str, str]
    ] = set()

    with SOURCE_FILE.open(
        "r",
        encoding=SOURCE_ENCODING,
    ) as file:
        for line_number, raw_line in enumerate(
            file,
            start=1,
        ):
            line = raw_line.strip()

            if not line:
                continue

            try:
                text, raw_label = line.rsplit(
                    "@",
                    maxsplit=1,
                )
            except ValueError as error:
                raise ValueError(
                    "Formato inválido en línea "
                    f"{line_number}"
                ) from error

            normalized_text = (
                " ".join(
                    text.split()
                )
                .strip()
            )

            normalized_label = (
                raw_label
                .strip()
                .lower()
            )

            label = LABEL_MAP.get(
                normalized_label
            )

            if label is None:
                raise ValueError(
                    "Etiqueta desconocida "
                    f"'{raw_label}' "
                    f"en línea {line_number}"
                )

            if not normalized_text:
                continue

            key = (
                normalized_text,
                label,
            )

            if key in seen:
                continue

            seen.add(key)

            samples.append(
                Sample(
                    text=normalized_text,
                    label=label,
                )
            )

    return samples


def stratified_split(
    samples: list[Sample],
) -> tuple[
    list[Sample],
    list[Sample],
    list[Sample],
]:
    grouped: dict[
        str,
        list[Sample],
    ] = {}

    for sample in samples:
        grouped.setdefault(
            sample.label,
            [],
        ).append(sample)

    random_generator = random.Random(
        RANDOM_SEED
    )

    train: list[Sample] = []
    validation: list[Sample] = []
    test: list[Sample] = []

    for label in sorted(
        grouped
    ):
        group = grouped[label][:]
        random_generator.shuffle(
            group
        )

        total = len(group)

        train_count = round(
            total * TRAIN_RATIO
        )

        validation_count = round(
            total * VALIDATION_RATIO
        )

        train.extend(
            group[:train_count]
        )

        validation.extend(
            group[
                train_count:
                train_count
                + validation_count
            ]
        )

        test.extend(
            group[
                train_count
                + validation_count:
            ]
        )

    random_generator.shuffle(
        train
    )

    random_generator.shuffle(
        validation
    )

    random_generator.shuffle(
        test
    )

    return (
        train,
        validation,
        test,
    )


def write_csv(
    path: Path,
    samples: list[Sample],
) -> None:
    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.writer(
            file
        )

        writer.writerow(
            [
                "text",
                "label",
            ]
        )

        for sample in samples:
            writer.writerow(
                [
                    sample.text,
                    sample.label,
                ]
            )


def print_distribution(
    name: str,
    samples: list[Sample],
) -> None:
    counts = Counter(
        sample.label
        for sample in samples
    )

    print(
        f"{name}: {len(samples)}"
    )

    for label in (
        "POSITIVO",
        "NEUTRAL",
        "NEGATIVO",
    ):
        count = counts.get(
            label,
            0,
        )

        percentage = (
            count
            / len(samples)
            * 100
            if samples
            else 0
        )

        print(
            f"  {label:<10}"
            f"{count:>5} "
            f"({percentage:6.2f}%)"
        )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    samples = read_samples()

    train, validation, test = (
        stratified_split(
            samples
        )
    )

    write_csv(
        NORMALIZED_FILE,
        samples,
    )

    write_csv(
        TRAIN_FILE,
        train,
    )

    write_csv(
        VALIDATION_FILE,
        validation,
    )

    write_csv(
        TEST_FILE,
        test,
    )

    print(
        "=" * 72
    )

    print(
        "ALPHAINVEST AI — "
        "FINANCIAL PHRASEBANK"
    )

    print(
        "=" * 72
    )

    print(
        "Source:",
        SOURCE_FILE,
    )

    print(
        "Seed:",
        RANDOM_SEED,
    )

    print()

    print_distribution(
        "TOTAL",
        samples,
    )

    print()

    print_distribution(
        "TRAIN",
        train,
    )

    print()

    print_distribution(
        "VALIDATION",
        validation,
    )

    print()

    print_distribution(
        "TEST",
        test,
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()