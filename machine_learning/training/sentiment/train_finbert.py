from __future__ import annotations

import argparse
import csv
import json
import random
import shutil
from collections import Counter
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
)
from torch import nn
from torch.optim import AdamW
from torch.utils.data import DataLoader, Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    get_linear_schedule_with_warmup,
)

MODEL_ID = "yiyanghkust/finbert-pretrain"

MODEL_REVISION = (
    "88ab954a39ea6d3ce2b62cff086dd5ad1172c664"
)

RANDOM_SEED = 42

MAX_LENGTH = 96
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
WEIGHT_DECAY = 0.01
MAX_EPOCHS = 3
EARLY_STOPPING_PATIENCE = 1
GRADIENT_CLIP_NORM = 1.0
PROGRESS_EVERY_BATCHES = 10

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

ID2LABEL = {
    index: label
    for label, index in LABEL2ID.items()
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

TRAIN_FILE = (
    DATASET_DIR
    / "train.csv"
)

VALIDATION_FILE = (
    DATASET_DIR
    / "validation.csv"
)

CACHE_DIR = (
    ROOT_DIR
    / "saved_models"
    / "huggingface"
)

CANDIDATE_DIR = (
    ROOT_DIR
    / "saved_models"
    / "sentiment"
    / "finbert_candidate"
)


class EncodedSentimentDataset(
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
    ) -> None:
        encoded = tokenizer(
            texts,
            padding="max_length",
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="pt",
        )

        self._inputs = encoded

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
        inputs = {
            key: value[index]
            for key, value
            in self._inputs.items()
        }

        return (
            inputs,
            self._labels[index],
        )


def set_seed() -> None:
    random.seed(
        RANDOM_SEED
    )

    np.random.seed(
        RANDOM_SEED
    )

    torch.manual_seed(
        RANDOM_SEED
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


def calculate_class_weights(
    labels: list[str],
) -> torch.Tensor:
    counts = Counter(
        labels
    )

    total = len(labels)

    weights = [
        total
        / (
            len(LABELS)
            * counts[label]
        )
        for label in LABELS
    ]

    return torch.tensor(
        weights,
        dtype=torch.float32,
    )


def move_inputs(
    inputs: dict[
        str,
        torch.Tensor,
    ],
    device: torch.device,
) -> dict[
    str,
    torch.Tensor,
]:
    return {
        key: value.to(
            device
        )
        for key, value
        in inputs.items()
    }


def evaluate(
    *,
    model,
    data_loader: DataLoader,
    device: torch.device,
) -> dict[str, object]:
    model.eval()

    predicted: list[int] = []
    actual: list[int] = []

    with torch.no_grad():
        for inputs, labels in data_loader:
            inputs = move_inputs(
                inputs,
                device,
            )

            outputs = model(
                **inputs
            )

            predictions = (
                outputs.logits.argmax(
                    dim=-1
                )
            )

            predicted.extend(
                predictions
                .cpu()
                .tolist()
            )

            actual.extend(
                labels.tolist()
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

    matrix = confusion_matrix(
        actual,
        predicted,
        labels=[
            0,
            1,
            2,
        ],
    )

    return {
        "accuracy": accuracy,
        "balanced_accuracy": (
            balanced_accuracy
        ),
        "macro_f1": macro_f1,
        "confusion_matrix": (
            matrix.tolist()
        ),
    }


def save_best_candidate(
    *,
    model,
    tokenizer,
    metrics: dict[str, object],
    epoch: int,
    smoke: bool,
) -> None:
    if CANDIDATE_DIR.exists():
        shutil.rmtree(
            CANDIDATE_DIR
        )

    CANDIDATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.save_pretrained(
        CANDIDATE_DIR,
        safe_serialization=True,
    )

    tokenizer.save_pretrained(
        CANDIDATE_DIR
    )

    metadata = {
        "model_id": MODEL_ID,
        "model_revision": (
            MODEL_REVISION
        ),
        "random_seed": (
            RANDOM_SEED
        ),
        "max_length": (
            MAX_LENGTH
        ),
        "batch_size": (
            BATCH_SIZE
        ),
        "learning_rate": (
            LEARNING_RATE
        ),
        "weight_decay": (
            WEIGHT_DECAY
        ),
        "max_epochs": (
            MAX_EPOCHS
        ),
        "best_epoch": epoch,
        "smoke": smoke,
        "labels": list(
            LABELS
        ),
        "validation_metrics": (
            metrics
        ),
    }

    metadata_path = (
        CANDIDATE_DIR
        / "training_metadata.json"
    )

    metadata_path.write_text(
        json.dumps(
            metadata,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--smoke",
        action="store_true",
        help=(
            "Ejecuta entrenamiento "
            "mínimo de validación."
        ),
    )

    args = parser.parse_args()

    set_seed()

    device = torch.device(
        "cpu"
    )

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=CACHE_DIR,
            local_files_only=True,
        )
    )

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

    epochs = MAX_EPOCHS

    if args.smoke:
        train_texts = (
            train_texts[:96]
        )

        train_labels = (
            train_labels[:96]
        )

        validation_texts = (
            validation_texts[:48]
        )

        validation_labels = (
            validation_labels[:48]
        )

        epochs = 1

    train_dataset = (
        EncodedSentimentDataset(
            texts=train_texts,
            labels=train_labels,
            tokenizer=tokenizer,
        )
    )

    validation_dataset = (
        EncodedSentimentDataset(
            texts=validation_texts,
            labels=validation_labels,
            tokenizer=tokenizer,
        )
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=0,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=0,
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=CACHE_DIR,
            local_files_only=True,
            num_labels=3,
            label2id=LABEL2ID,
            id2label=ID2LABEL,
        )
    )

    model.to(
        device
    )

    class_weights = (
        calculate_class_weights(
            train_labels
        )
        .to(device)
    )

    loss_function = (
        nn.CrossEntropyLoss(
            weight=class_weights
        )
    )

    optimizer = AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    total_steps = (
        len(train_loader)
        * epochs
    )

    warmup_steps = int(
        total_steps
        * 0.10
    )

    scheduler = (
        get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=(
                warmup_steps
            ),
            num_training_steps=(
                total_steps
            ),
        )
    )

    print("=" * 72)

    print(
        "ALPHAINVEST AI — "
        "FINBERT TRAINING"
    )

    print("=" * 72)

    print(
        "Mode:",
        (
            "SMOKE"
            if args.smoke
            else "FULL"
        ),
    )

    print(
        "Device:",
        device,
    )

    print(
        "Train:",
        len(train_dataset),
    )

    print(
        "Validation:",
        len(validation_dataset),
    )

    print(
        "Max length:",
        MAX_LENGTH,
    )

    print(
        "Batch size:",
        BATCH_SIZE,
    )

    print(
        "Epochs:",
        epochs,
    )

    print(
        "Class weights:",
        [
            round(
                float(value),
                4,
            )
            for value
            in class_weights.cpu()
        ],
    )

    print("=" * 72)

    best_macro_f1 = -1.0

    epochs_without_improvement = 0

    for epoch in range(
        1,
        epochs + 1,
    ):
        model.train()

        running_loss = 0.0

        epoch_start = perf_counter()

        total_batches = len(
            train_loader
        )

        for (
            batch_index,
            (
                inputs,
                labels,
            ),
        ) in enumerate(
            train_loader,
            start=1,
        ):
            inputs = move_inputs(
                inputs,
                device,
            )

            labels = labels.to(
                device
            )

            optimizer.zero_grad(
                set_to_none=True
            )

            outputs = model(
                **inputs
            )

            loss = loss_function(
                outputs.logits,
                labels,
            )

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                model.parameters(),
                GRADIENT_CLIP_NORM,
            )

            optimizer.step()
            scheduler.step()

            batch_loss = float(
                loss.detach().cpu()
            )

            running_loss += (
                batch_loss
            )

            should_report = (
                batch_index == 1
                or batch_index
                % PROGRESS_EVERY_BATCHES
                == 0
                or batch_index
                == total_batches
            )

            if should_report:
                elapsed_seconds = (
                    perf_counter()
                    - epoch_start
                )

                seconds_per_batch = (
                    elapsed_seconds
                    / batch_index
                )

                remaining_batches = (
                    total_batches
                    - batch_index
                )

                estimated_remaining = (
                    seconds_per_batch
                    * remaining_batches
                )

                progress = (
                    batch_index
                    / total_batches
                    * 100
                )

                average_loss = (
                    running_loss
                    / batch_index
                )

                print(
                    (
                        "Training "
                        f"{batch_index:>4}/"
                        f"{total_batches} "
                        f"[{progress:6.2f}%] "
                        f"loss={average_loss:.4f} "
                        f"batch={seconds_per_batch:.2f}s "
                        f"ETA={estimated_remaining / 60:.1f}m"
                    ),
                    flush=True,
                )

        train_loss = (
            running_loss
            / len(train_loader)
        )

        print(
            (
                "Training epoch terminado. "
                "Iniciando validation..."
            ),
            flush=True,
        )

        metrics = evaluate(
            model=model,
            data_loader=(
                validation_loader
            ),
            device=device,
        )

        print()

        print(
            f"Epoch {epoch}/{epochs}"
        )

        print(
            "Train loss:",
            f"{train_loss:.4f}",
        )

        print(
            "Validation accuracy:",
            (
                f"{metrics['accuracy']:.4f}"
            ),
        )

        print(
            "Validation balanced accuracy:",
            (
                f"{metrics['balanced_accuracy']:.4f}"
            ),
        )

        print(
            "Validation macro F1:",
            f"{metrics['macro_f1']:.4f}",
        )

        print(
            "Confusion matrix:"
        )

        for (
            label,
            row,
        ) in zip(
            LABELS,
            metrics[
                "confusion_matrix"
            ],
            strict=True,
        ):
            print(
                f"{label:<10}",
                tuple(row),
            )

        macro_f1 = float(
            metrics[
                "macro_f1"
            ]
        )

        if (
            macro_f1
            > best_macro_f1
        ):
            best_macro_f1 = (
                macro_f1
            )

            epochs_without_improvement = 0

            save_best_candidate(
                model=model,
                tokenizer=tokenizer,
                metrics=metrics,
                epoch=epoch,
                smoke=args.smoke,
            )

            print(
                "Best candidate saved."
            )

        else:
            epochs_without_improvement += 1

            if (
                epochs_without_improvement
                >= EARLY_STOPPING_PATIENCE
            ):
                print(
                    "Early stopping."
                )

                break

    print()

    print(
        "Best validation macro F1:",
        f"{best_macro_f1:.4f}",
    )

    print(
        "Candidate:",
        CANDIDATE_DIR,
    )

    print("=" * 72)


if __name__ == "__main__":
    main()