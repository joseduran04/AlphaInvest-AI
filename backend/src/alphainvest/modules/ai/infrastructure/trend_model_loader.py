import hashlib
from pathlib import Path

from xgboost import XGBClassifier

from alphainvest.modules.ai.domain.exceptions import (
    AIArtifactIntegrityError,
    AIArtifactLoadError,
    AIArtifactNotFoundError,
)
from alphainvest.modules.ai.domain.loaded_model import (
    LoadedTrendModel,
)
from alphainvest.modules.ai.infrastructure.models import (
    ModelVersionModel,
)


class TrendModelLoader:
    """Carga artefactos XGBoost verificando su integridad."""

    @classmethod
    def load(
        cls,
        version: ModelVersionModel,
    ) -> LoadedTrendModel:
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

        classifier = XGBClassifier()

        try:
            classifier.load_model(
                artifact_path
            )
        except Exception as error:
            raise AIArtifactLoadError(
                "El artefacto registrado no pudo "
                "cargarse como modelo XGBoost"
            ) from error

        return LoadedTrendModel(
            version_id=version.id,
            model_id=version.modelo_id,
            version=version.version,
            artifact_path=artifact_path,
            checksum=actual_checksum,
            classifier=classifier,
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