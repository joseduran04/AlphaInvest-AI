from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from uuid import UUID


@dataclass(frozen=True, slots=True)
class LoadedPriceForecastModel:
    """Pronóstico de precio cargado y verificado."""

    version_id: UUID
    model_id: UUID
    version: str

    artifact_path: Path
    checksum: str

    algorithm: str
    framework: str

    horizon_sessions: int
    median_return_percentage: Decimal
    calibration_rows: int
    source_name: str