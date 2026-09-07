import hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pytest
from xgboost import XGBClassifier

from alphainvest.modules.ai.domain.exceptions import (
    AIArtifactIntegrityError,
    AIArtifactLoadError,
    AIArtifactNotFoundError,
)
from alphainvest.modules.ai.infrastructure.trend_model_loader import (
    TrendModelLoader,
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
) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        version="0.1.0",
        ruta_artefacto=str(artifact_path),
        checksum=checksum,
    )


def test_rejects_missing_artifact(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.ubj"

    version = build_version(
        artifact_path=missing,
        checksum="abc",
    )

    with pytest.raises(
        AIArtifactNotFoundError
    ):
        TrendModelLoader.load(version)


def test_rejects_invalid_checksum(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "model.ubj"

    artifact.write_bytes(
        b"invalid-model"
    )

    version = build_version(
        artifact_path=artifact,
        checksum="wrong-checksum",
    )

    with pytest.raises(
        AIArtifactIntegrityError
    ):
        TrendModelLoader.load(version)


def test_rejects_invalid_xgboost_artifact(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "model.ubj"

    artifact.write_bytes(
        b"not-an-xgboost-model"
    )

    version = build_version(
        artifact_path=artifact,
        checksum=calculate_checksum(
            artifact
        ),
    )

    with pytest.raises(
        AIArtifactLoadError
    ):
        TrendModelLoader.load(version)


def test_loads_verified_model(
    tmp_path: Path,
) -> None:
    artifact = tmp_path / "model.ubj"

    artifact.write_bytes(
        b"verified-model"
    )

    checksum = calculate_checksum(
        artifact
    )

    version = build_version(
        artifact_path=artifact,
        checksum=checksum,
    )

    XGBClassifier()

    with patch.object(
        XGBClassifier,
        "load_model",
    ) as load_model:
        loaded = TrendModelLoader.load(
            version
        )

    load_model.assert_called_once()

    assert loaded.version_id == version.id
    assert loaded.model_id == version.modelo_id
    assert loaded.version == "0.1.0"
    assert loaded.checksum == checksum
    assert loaded.artifact_path == artifact