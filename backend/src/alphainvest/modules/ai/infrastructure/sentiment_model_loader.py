import hashlib
from pathlib import Path

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

from alphainvest.modules.ai.domain.exceptions import (
    AIArtifactIntegrityError,
    AIArtifactLoadError,
    AIArtifactNotFoundError,
)
from alphainvest.modules.ai.domain.loaded_sentiment_model import (
    LoadedSentimentModel,
)
from alphainvest.modules.ai.infrastructure.models import (
    ModelVersionModel,
)


class SentimentModelLoader:
    """Carga FinBERT local verificando contrato e integridad."""

    MODEL_CODE = "ANALISIS_SENTIMIENTO"

    ALGORITHM = (
        "FINBERT_SEQUENCE_CLASSIFICATION"
    )

    FRAMEWORK = "transformers+pytorch"

    EXPECTED_LABELS = {
        0: "NEGATIVO",
        1: "NEUTRAL",
        2: "POSITIVO",
    }

    REQUIRED_FILES = (
        "config.json",
        "tokenizer_config.json",
        "vocab.txt",
    )

    @classmethod
    def load(
        cls,
        version: ModelVersionModel,
    ) -> LoadedSentimentModel:
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
            version.checksum
            .strip()
            .lower()
        )

        if actual_checksum != expected_checksum:
            raise AIArtifactIntegrityError(
                "El checksum SHA-256 del artefacto "
                "de sentimiento no coincide "
                "con el registrado"
            )

        cls._validate_registration(
            version
        )

        model_directory = (
            artifact_path.parent
        )

        cls._validate_model_directory(
            model_directory
        )

        try:
            tokenizer = (
                AutoTokenizer
                .from_pretrained(  # type: ignore[no-untyped-call]
                    model_directory,
                    local_files_only=True,
                )
            )

            classifier = (
                AutoModelForSequenceClassification
                .from_pretrained(
                    model_directory,
                    local_files_only=True,
                )
            )

        except Exception as error:
            raise AIArtifactLoadError(
                "El artefacto de sentimiento "
                "no pudo cargarse localmente"
            ) from error

        cls._validate_loaded_model(
            classifier
        )

        classifier.eval()

        return LoadedSentimentModel(
            version_id=version.id,
            model_id=version.modelo_id,
            version=version.version,
            artifact_path=artifact_path,
            checksum=actual_checksum,
            algorithm=cls.ALGORITHM,
            framework=cls.FRAMEWORK,
            tokenizer=tokenizer,
            classifier=classifier,
        )

    @classmethod
    def _validate_registration(
        cls,
        version: ModelVersionModel,
    ) -> None:
        if (
            version.algoritmo.strip()
            != cls.ALGORITHM
        ):
            raise AIArtifactLoadError(
                "El algoritmo registrado en PostgreSQL "
                "no corresponde al runtime "
                "de sentimiento"
            )

        if (
            version.framework is None
            or version.framework.strip()
            != cls.FRAMEWORK
        ):
            raise AIArtifactLoadError(
                "El framework registrado en PostgreSQL "
                "no corresponde al runtime "
                "de sentimiento"
            )

    @classmethod
    def _validate_model_directory(
        cls,
        directory: Path,
    ) -> None:
        for file_name in cls.REQUIRED_FILES:
            required_path = (
                directory
                / file_name
            )

            if not required_path.is_file():
                raise AIArtifactNotFoundError(
                    "Falta un archivo requerido "
                    "del modelo de sentimiento: "
                    f"{required_path.as_posix()}"
                )

    @classmethod
    def _validate_loaded_model(
        cls,
        classifier: object,
    ) -> None:
        config = getattr(
            classifier,
            "config",
            None,
        )

        if config is None:
            raise AIArtifactLoadError(
                "El modelo cargado no contiene "
                "configuración"
            )

        num_labels = getattr(
            config,
            "num_labels",
            None,
        )

        if num_labels != 3:
            raise AIArtifactLoadError(
                "El modelo de sentimiento no contiene "
                "exactamente tres clases"
            )

        raw_labels = getattr(
            config,
            "id2label",
            None,
        )

        if not isinstance(
            raw_labels,
            dict,
        ):
            raise AIArtifactLoadError(
                "El modelo de sentimiento no contiene "
                "un mapeo id2label válido"
            )

        normalized_labels = {
            int(key): str(value)
            for key, value
            in raw_labels.items()
        }

        if (
            normalized_labels
            != cls.EXPECTED_LABELS
        ):
            raise AIArtifactLoadError(
                "Las clases del modelo no coinciden "
                "con NEGATIVO/NEUTRAL/POSITIVO"
            )

    @staticmethod
    def calculate_sha256(
        path: Path,
    ) -> str:
        digest = hashlib.sha256()

        try:
            with path.open(
                "rb"
            ) as file:
                for chunk in iter(
                    lambda: file.read(
                        1024 * 1024
                    ),
                    b"",
                ):
                    digest.update(
                        chunk
                    )

        except OSError as error:
            raise AIArtifactLoadError(
                "No fue posible leer el artefacto "
                "del modelo de sentimiento"
            ) from error

        return digest.hexdigest()