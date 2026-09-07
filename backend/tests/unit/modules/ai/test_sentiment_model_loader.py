import hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from alphainvest.modules.ai.domain.exceptions import (
    AIArtifactIntegrityError,
    AIArtifactLoadError,
    AIArtifactNotFoundError,
)
from alphainvest.modules.ai.infrastructure.sentiment_model_loader import (
    SentimentModelLoader,
)

pytestmark = pytest.mark.unit


def calculate_checksum(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def build_version(
    *,
    artifact_path: Path,
    checksum: str,
    algorithm: str = (
        "FINBERT_SEQUENCE_CLASSIFICATION"
    ),
    framework: str = (
        "transformers+pytorch"
    ),
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        version="0.1.0",
        ruta_artefacto=str(
            artifact_path
        ),
        checksum=checksum,
        algoritmo=algorithm,
        framework=framework,
    )


def create_required_files(
    directory: Path,
) -> None:
    for file_name in (
        "config.json",
        "tokenizer_config.json",
        "vocab.txt",
    ):
        (
            directory
            / file_name
        ).write_text(
            "{}",
            encoding="utf-8",
        )


def test_rejects_missing_artifact(
    tmp_path: Path,
) -> None:
    version = build_version(
        artifact_path=(
            tmp_path
            / "model.safetensors"
        ),
        checksum="abc",
    )

    with pytest.raises(
        AIArtifactNotFoundError
    ):
        SentimentModelLoader.load(
            version
        )


def test_rejects_invalid_checksum(
    tmp_path: Path,
) -> None:
    artifact = (
        tmp_path
        / "model.safetensors"
    )

    artifact.write_bytes(
        b"model"
    )

    version = build_version(
        artifact_path=artifact,
        checksum="invalid",
    )

    with pytest.raises(
        AIArtifactIntegrityError
    ):
        SentimentModelLoader.load(
            version
        )


def test_rejects_wrong_algorithm(
    tmp_path: Path,
) -> None:
    artifact = (
        tmp_path
        / "model.safetensors"
    )

    artifact.write_bytes(
        b"model"
    )

    create_required_files(
        tmp_path
    )

    version = build_version(
        artifact_path=artifact,
        checksum=calculate_checksum(
            artifact
        ),
        algorithm="OTRO_MODELO",
    )

    with pytest.raises(
        AIArtifactLoadError
    ):
        SentimentModelLoader.load(
            version
        )


def test_rejects_missing_model_file(
    tmp_path: Path,
) -> None:
    artifact = (
        tmp_path
        / "model.safetensors"
    )

    artifact.write_bytes(
        b"model"
    )

    version = build_version(
        artifact_path=artifact,
        checksum=calculate_checksum(
            artifact
        ),
    )

    with pytest.raises(
        AIArtifactNotFoundError
    ):
        SentimentModelLoader.load(
            version
        )


def test_loads_verified_sentiment_model(
    tmp_path: Path,
) -> None:
    artifact = (
        tmp_path
        / "model.safetensors"
    )

    artifact.write_bytes(
        b"verified-model"
    )

    create_required_files(
        tmp_path
    )

    checksum = calculate_checksum(
        artifact
    )

    version = build_version(
        artifact_path=artifact,
        checksum=checksum,
    )

    tokenizer = MagicMock()

    classifier = MagicMock()

    classifier.config.num_labels = 3

    classifier.config.id2label = {
        0: "NEGATIVO",
        1: "NEUTRAL",
        2: "POSITIVO",
    }

    with (
        patch(
            (
                "alphainvest.modules.ai."
                "infrastructure."
                "sentiment_model_loader."
                "AutoTokenizer."
                "from_pretrained"
            ),
            return_value=tokenizer,
        ),
        patch(
            (
                "alphainvest.modules.ai."
                "infrastructure."
                "sentiment_model_loader."
                "AutoModelForSequenceClassification."
                "from_pretrained"
            ),
            return_value=classifier,
        ),
    ):
        loaded = (
            SentimentModelLoader
            .load(
                version
            )
        )

    assert (
        loaded.version_id
        == version.id
    )

    assert (
        loaded.model_id
        == version.modelo_id
    )

    assert loaded.version == "0.1.0"

    assert (
        loaded.artifact_path
        == artifact
    )

    assert loaded.checksum == checksum

    assert (
        loaded.algorithm
        == "FINBERT_SEQUENCE_CLASSIFICATION"
    )

    assert (
        loaded.framework
        == "transformers+pytorch"
    )

    assert (
        loaded.tokenizer
        is tokenizer
    )

    assert (
        loaded.classifier
        is classifier
    )

    classifier.eval.assert_called_once()