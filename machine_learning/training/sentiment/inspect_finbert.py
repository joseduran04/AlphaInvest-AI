from __future__ import annotations

import os
from pathlib import Path

from transformers import (
    AutoConfig,
    AutoTokenizer,
)

MODEL_ID = (
    "yiyanghkust/finbert-pretrain"
)

MODEL_REVISION = (
    "88ab954a39ea6d3ce2b62cff086dd5ad1172c664"
)


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
    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    os.environ[
        "HF_HOME"
    ] = str(
        CACHE_DIR
    )

    config = (
        AutoConfig.from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=CACHE_DIR,
        )
    )

    tokenizer = (
        AutoTokenizer
        .from_pretrained(
            MODEL_ID,
            revision=MODEL_REVISION,
            cache_dir=CACHE_DIR,
        )
    )

    print(
        "=" * 72
    )

    print(
        "ALPHAINVEST AI — "
        "FINBERT INSPECTION"
    )

    print(
        "=" * 72
    )

    print(
        "Model:",
        MODEL_ID,
    )

    print(
        "Revision:",
        MODEL_REVISION,
    )

    print(
        "Architecture:",
        config.architectures,
    )

    print(
        "Hidden size:",
        config.hidden_size,
    )

    print(
        "Layers:",
        config.num_hidden_layers,
    )

    print(
        "Attention heads:",
        config.num_attention_heads,
    )

    print(
        "Max positions:",
        config.max_position_embeddings,
    )

    print(
        "Vocabulary:",
        len(tokenizer),
    )

    print()

    sample = (
        "The company reported "
        "strong earnings growth."
    )

    encoded = tokenizer(
        sample,
        truncation=True,
        max_length=128,
    )

    print(
        "Sample tokens:",
        len(
            encoded[
                "input_ids"
            ]
        ),
    )

    print(
        "=" * 72
    )


if __name__ == "__main__":
    main()