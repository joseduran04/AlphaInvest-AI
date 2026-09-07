from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from transformers import (
    PreTrainedModel,
    PreTrainedTokenizerBase,
)


@dataclass(frozen=True, slots=True)
class LoadedSentimentModel:
    """Modelo NLP de sentimiento cargado y verificado."""

    version_id: UUID
    model_id: UUID
    version: str

    artifact_path: Path
    checksum: str

    algorithm: str
    framework: str

    tokenizer: PreTrainedTokenizerBase
    classifier: PreTrainedModel