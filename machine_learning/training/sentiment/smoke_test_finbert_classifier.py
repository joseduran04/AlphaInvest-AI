from __future__ import annotations

from pathlib import Path

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

MODEL_ID = "yiyanghkust/finbert-pretrain"

MODEL_REVISION = (
    "88ab954a39ea6d3ce2b62cff086dd5ad1172c664"
)


LABEL2ID = {
    "NEGATIVO": 0,
    "NEUTRAL": 1,
    "POSITIVO": 2,
}

ID2LABEL = {
    value: key
    for key, value in LABEL2ID.items()
}


ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

CACHE_DIR = (
    ROOT_DIR
    / "saved_models"
    / "huggingface"
)


def main() -> None:
    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=CACHE_DIR,
        )
    )

    model = (
        AutoModelForSequenceClassification
        .from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=CACHE_DIR,
            num_labels=3,
            label2id=LABEL2ID,
            id2label=ID2LABEL,
        )
    )

    model.eval()

    texts = [
        (
            "The company reported "
            "strong earnings growth."
        ),
        (
            "The company announced "
            "quarterly results."
        ),
        (
            "Sales declined and the "
            "company lowered guidance."
        ),
    ]

    inputs = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors="pt",
    )

    with torch.no_grad():
        output = model(
            **inputs
        )

    logits = output.logits

    probabilities = (
        torch.softmax(
            logits,
            dim=-1,
        )
    )

    print("=" * 72)

    print(
        "ALPHAINVEST AI — "
        "FINBERT CLASSIFIER SMOKE TEST"
    )

    print("=" * 72)

    print(
        "Device:",
        next(
            model.parameters()
        ).device,
    )

    print(
        "Num labels:",
        model.config.num_labels,
    )

    print(
        "Label map:",
        model.config.id2label,
    )

    print(
        "Input shape:",
        tuple(
            inputs[
                "input_ids"
            ].shape
        ),
    )

    print(
        "Logits shape:",
        tuple(
            logits.shape
        ),
    )

    print()

    for text, row in zip(
        texts,
        probabilities,
        strict=True,
    ):
        print(text)

        print(
            {
                ID2LABEL[index]: round(
                    float(value),
                    4,
                )
                for index, value
                in enumerate(
                    row.tolist()
                )
            }
        )

        print()

    print("=" * 72)


if __name__ == "__main__":
    main()