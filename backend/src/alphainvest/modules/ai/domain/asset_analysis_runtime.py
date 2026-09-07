from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AssetAnalysisRuntime:
    """Dependencias técnicas resueltas para análisis ACTIVO."""

    trend_version_id: UUID
    price_forecast_version_id: UUID

    price_source_id: UUID

    trend_version: str
    price_forecast_version: str

    price_source_name: str