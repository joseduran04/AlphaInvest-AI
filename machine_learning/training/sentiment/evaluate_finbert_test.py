from __future__ import annotations

import csv
import json
from pathlib import Path

import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

LABELS = (
    "NEGATIVO",
    "NEUTRAL",
    "POSITIVO",
)

LABEL2ID = {
    label: index
    for index, label in enumerate(
        LABELS
    )
}


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

TEST_FILE = (
    DATASET_DIR
    / "test.csv"
)

CANDIDATE_DIR = (
    ROOT_DIR
    / "saved_models"
    / "sentiment"
    / "finbert_candidate"
)

METADATA_FILE = (
    CANDIDATE_DIR
    / "training_metadata.json"
)


class TestDataset(
    Dataset[
        tuple[
            dict[str, torch.Tensor],
            torch.Tensor,
        ]
    ]
):
    def __init__(
        self,
        *,
        texts: list[str],
        labels: list[str],
        tokenizer,
        max_length: int,
    ) -> None:
        self._inputs = tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )

        self._labels = torch.tensor(
            [
                LABEL2ID[label]
                for label in labels
            ],
            dtype=torch.long,
        )

    def __len__(self) -> int:
        return len(
            self._labels
        )

    def __getitem__(
        self,
        index: int,
    ) -> tuple[
        dict[str, torch.Tensor],
        torch.Tensor,
    ]:
        return (
            {
                key: value[index]
                for key, value
                in self._inputs.items()
            },
            self._labels[index],
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

    return texts, labels


def main() -> None:
    metadata = json.loads(
        METADATA_FILE.read_text(
            encoding="utf-8"
        )
    )

    if metadata.get("smoke") is not False:
        raise RuntimeError(
            "El candidato no corresponde "
            "a un entrenamiento FULL"
        )

    max_length = int(
        metadata["max_length"]
    )

    batch_size = int(
        metadata["batch_size"]
    )

    texts, labels = read_dataset(
        TEST_FILE
    )

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            CANDIDATE_DIR,
            local_files_only=True,
        )
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            CANDIDATE_DIR,
            local_files_only=True,
        )
    )

    model.eval()

    device = torch.device(
        "cpu"
    )

    model.to(
        device
    )

    dataset = TestDataset(
        texts=texts,
        labels=labels,
        tokenizer=tokenizer,
        max_length=max_length,
    )

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )

    predicted: list[int] = []
    actual: list[int] = []

    with torch.no_grad():
        for inputs, batch_labels in loader:
            inputs = {
                key: value.to(
                    device
                )
                for key, value
                in inputs.items()
            }

            outputs = model(
                **inputs
            )

            predictions = (
                outputs.logits
                .argmax(
                    dim=-1
                )
            )

            predicted.extend(
                predictions
                .cpu()
                .tolist()
            )

            actual.extend(
                batch_labels.tolist()
            )

    accuracy = float(
        accuracy_score(
            actual,
            predicted,
        )
    )

    balanced_accuracy = float(
        balanced_accuracy_score(
            actual,
            predicted,
        )
    )

    macro_f1 = float(
        f1_score(
            actual,
            predicted,
            labels=[
                0,
                1,
                2,
            ],
            average="macro",
            zero_division=0,
        )
    )

    (
        precision,
        recall,
        class_f1,
        support,
    ) = (
        precision_recall_fscore_support(
            actual,
            predicted,
            labels=[
                0,
                1,
                2,
            ],
            zero_division=0,
        )
    )

    matrix = confusion_matrix(
        actual,
        predicted,
        labels=[
            0,
            1,
            2,
        ],
    )

    print("=" * 72)

    print(
        "ALPHAINVEST AI — "
        "FINBERT FINAL TEST"
    )

    print("=" * 72)

    print(
        "Test:",
        len(dataset),
    )

    print(
        "Best epoch:",
        metadata[
            "best_epoch"
        ],
    )

    print(
        "Validation macro F1:",
        (
            f"{metadata['validation_metrics']['macro_f1']:.4f}"
        ),
    )

    print()

    print(
        f"Test accuracy:          "
        f"{accuracy:.4f}"
    )

    print(
        f"Test balanced accuracy: "
        f"{balanced_accuracy:.4f}"
    )

    print(
        f"Test macro F1:          "
        f"{macro_f1:.4f}"
    )

    print()

    print(
        "Per-class metrics:"
    )

    for index, label in enumerate(
        LABELS
    ):
        print(
            
                f"{label:<10} "
                f"precision={precision[index]:.4f} "
                f"recall={recall[index]:.4f} "
                f"f1={class_f1[index]:.4f} "
                f"support={int(support[index])}"
            
        )

    print()

    print(
        "Confusion matrix:"
    )

    for label, row in zip(
        LABELS,
        matrix.tolist(),
        strict=True,
    ):
        print(
            f"{label:<10}",
            tuple(
                int(value)
                for value in row
            ),
        )

    print("=" * 72)


if __name__ == "__main__":
    main()