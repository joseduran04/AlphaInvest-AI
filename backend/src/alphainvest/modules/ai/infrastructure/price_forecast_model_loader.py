import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from alphainvest.modules.ai.domain.exceptions import (
    AIArtifactIntegrityError,
    AIArtifactLoadError,
    AIArtifactNotFoundError,
)
from alphainvest.modules.ai.domain.loaded_price_forecast_model import (
    LoadedPriceForecastModel,
)
from alphainvest.modules.ai.infrastructure.models import (
    ModelVersionModel,
)


class PriceForecastModelLoader:
    """Carga artefactos JSON de pronóstico verificando integridad."""

    MODEL_CODE = "PRONOSTICO_PRECIO"
    ALGORITHM = "HISTORICAL_MEDIAN_RETURN"
    FRAMEWORK = "ALPHAINVEST_NATIVE"

    @classmethod
    def load(
        cls,
        version: ModelVersionModel,
    ) -> LoadedPriceForecastModel:
        artifact_path = Path(
            version.ruta_artefacto
        )

        if not artifact_path.is_file():
            raise AIArtifactNotFoundError(
                "El artefacto registrado no existe: "
                f"{artifact_path.as_posix()}"
            )

        actual_checksum = cls.calculate_sha256(
            artifact_path
        )

        expected_checksum = (
            version.checksum.strip().lower()
        )

        if actual_checksum != expected_checksum:
            raise AIArtifactIntegrityError(
                "El checksum SHA-256 del artefacto "
                "no coincide con el registrado"
            )

        content = cls._load_json(
            artifact_path
        )

        cls._validate_identity(
            content=content,
            version=version,
        )

        horizon_sessions = cls._read_positive_int(
            content=content,
            key="horizon_sessions",
        )

        calibration_rows = cls._read_positive_int(
            content=content,
            key="calibration_rows",
        )

        median_return = cls._read_decimal(
            content=content,
            key="median_return_percentage",
        )

        source_name = cls._read_non_empty_string(
            content=content,
            key="source_name",
        )

        return LoadedPriceForecastModel(
            version_id=version.id,
            model_id=version.modelo_id,
            version=version.version,
            artifact_path=artifact_path,
            checksum=actual_checksum,
            algorithm=cls.ALGORITHM,
            framework=cls.FRAMEWORK,
            horizon_sessions=horizon_sessions,
            median_return_percentage=median_return,
            calibration_rows=calibration_rows,
            source_name=source_name,
        )

    @staticmethod
    def calculate_sha256(
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        try:
            with path.open("rb") as file:
                for chunk in iter(
                    lambda: file.read(
                        1024 * 1024
                    ),
                    b"",
                ):
                    digest.update(chunk)

        except OSError as error:
            raise AIArtifactLoadError(
                "No fue posible leer el artefacto "
                "del modelo"
            ) from error

        return digest.hexdigest()

    @staticmethod
    def _load_json(
        path: Path,
    ) -> dict[str, Any]:
        try:
            raw = path.read_text(
                encoding="utf-8"
            )

            content = json.loads(raw)

        except (
            OSError,
            UnicodeError,
            json.JSONDecodeError,
        ) as error:
            raise AIArtifactLoadError(
                "El artefacto registrado no pudo "
                "cargarse como JSON"
            ) from error

        if not isinstance(content, dict):
            raise AIArtifactLoadError(
                "El artefacto JSON debe contener "
                "un objeto en su raíz"
            )

        return content

    @classmethod
    def _validate_identity(
        cls,
        *,
        content: dict[str, Any],
        version: ModelVersionModel,
    ) -> None:
        model_code = cls._read_non_empty_string(
            content=content,
            key="model_code",
        )

        model_version = cls._read_non_empty_string(
            content=content,
            key="model_version",
        )

        algorithm = cls._read_non_empty_string(
            content=content,
            key="algorithm",
        )

        framework = cls._read_non_empty_string(
            content=content,
            key="framework",
        )

        if model_code != cls.MODEL_CODE:
            raise AIArtifactLoadError(
                "El artefacto no corresponde a "
                "PRONOSTICO_PRECIO"
            )

        if model_version != version.version:
            raise AIArtifactLoadError(
                "La versión declarada por el artefacto "
                "no coincide con PostgreSQL"
            )

        if algorithm != cls.ALGORITHM:
            raise AIArtifactLoadError(
                "El algoritmo del artefacto "
                "no es compatible"
            )

        if framework != cls.FRAMEWORK:
            raise AIArtifactLoadError(
                "El framework del artefacto "
                "no es compatible"
            )

        if (
            version.algoritmo.strip()
            != cls.ALGORITHM
        ):
            raise AIArtifactLoadError(
                "El algoritmo registrado en PostgreSQL "
                "no coincide con el runtime"
            )

        if (
            version.framework is None
            or version.framework.strip()
            != cls.FRAMEWORK
        ):
            raise AIArtifactLoadError(
                "El framework registrado en PostgreSQL "
                "no coincide con el runtime"
            )

    @staticmethod
    def _read_non_empty_string(
        *,
        content: dict[str, Any],
        key: str,
    ) -> str:
        value = content.get(key)

        if (
            not isinstance(value, str)
            or not value.strip()
        ):
            raise AIArtifactLoadError(
                f"El artefacto no contiene "
                f"un valor válido para {key}"
            )

        return value.strip()

    @staticmethod
    def _read_positive_int(
        *,
        content: dict[str, Any],
        key: str,
    ) -> int:
        value = content.get(key)

        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value <= 0
        ):
            raise AIArtifactLoadError(
                f"El artefacto no contiene "
                f"un entero positivo para {key}"
            )

        return value

    @staticmethod
    def _read_decimal(
        *,
        content: dict[str, Any],
        key: str,
    ) -> Decimal:
        value = content.get(key)

        if isinstance(value, bool):
            raise AIArtifactLoadError(
                f"El artefacto no contiene "
                f"un decimal válido para {key}"
            )

        try:
            decimal_value = Decimal(
                str(value)
            )

        except (
            InvalidOperation,
            ValueError,
            TypeError,
        ) as error:
            raise AIArtifactLoadError(
                f"El artefacto no contiene "
                f"un decimal válido para {key}"
            ) from error

        if not decimal_value.is_finite():
            raise AIArtifactLoadError(
                f"El artefacto contiene "
                f"un decimal no finito para {key}"
            )

        return decimal_value