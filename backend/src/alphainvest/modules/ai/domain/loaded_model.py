from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from xgboost import XGBClassifier


@dataclass(frozen=True, slots=True)
class LoadedTrendModel:
    """Modelo de tendencia cargado y verificado."""

    version_id: UUID
    model_id: UUID
    version: str
    artifact_path: Path
    checksum: str
    classifier: XGBClassifier