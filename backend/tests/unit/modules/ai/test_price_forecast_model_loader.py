import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from alphainvest.modules.ai.domain.exceptions import (
    AIArtifactIntegrityError,
    AIArtifactLoadError,
    AIArtifactNotFoundError,
)
from alphainvest.modules.ai.infrastructure.price_forecast_model_loader import (
    PriceForecastModelLoader,
)

pytestmark = pytest.mark.unit


def build_artifact(
    tmp_path: Path,
) -> tuple[Path, str]:
    path = tmp_path / "model.json"

    content = {
        "algorithm": "HISTORICAL_MEDIAN_RETURN",
        "framework": "ALPHAINVEST_NATIVE",
        "model_code": "PRONOSTICO_PRECIO",
        "model_version": "0.1.0",
        "horizon_sessions": 5,
        "median_return_percentage": (
            0.7465371077185751
        ),
        "calibration_rows": 5631,
        "source_name": "Yahoo Finance",
        "target": "future_return_percentage",
    }

    path.write_text(
        json.dumps(
            content,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    checksum = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    return path, checksum


def test_loads_valid_artifact(
    tmp_path: Path,
) -> None:
    path, checksum = build_artifact(
        tmp_path
    )

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        version="0.1.0",
        ruta_artefacto=str(path),
        checksum=checksum,
        algoritmo="HISTORICAL_MEDIAN_RETURN",
        framework="ALPHAINVEST_NATIVE",
    )

    loaded = PriceForecastModelLoader.load(
        version
    )

    assert loaded.version == "0.1.0"

    assert (
        loaded.horizon_sessions
        == 5
    )

    assert (
        str(
            loaded.median_return_percentage
        )
        == "0.7465371077185751"
    )

    assert loaded.checksum == checksum


def test_rejects_missing_artifact(
    tmp_path: Path,
) -> None:
    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        version="0.1.0",
        ruta_artefacto=str(
            tmp_path / "missing.json"
        ),
        checksum="abc",
        algoritmo="HISTORICAL_MEDIAN_RETURN",
        framework="ALPHAINVEST_NATIVE",
    )

    with pytest.raises(
        AIArtifactNotFoundError
    ):
        PriceForecastModelLoader.load(
            version
        )


def test_rejects_invalid_checksum(
    tmp_path: Path,
) -> None:
    path, _ = build_artifact(
        tmp_path
    )

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        version="0.1.0",
        ruta_artefacto=str(path),
        checksum="invalid",
        algoritmo="HISTORICAL_MEDIAN_RETURN",
        framework="ALPHAINVEST_NATIVE",
    )

    with pytest.raises(
        AIArtifactIntegrityError
    ):
        PriceForecastModelLoader.load(
            version
        )


def test_rejects_invalid_contract(
    tmp_path: Path,
) -> None:
    path = tmp_path / "model.json"

    path.write_text(
        json.dumps(
            {
                "model_code": "OTRO_MODELO"
            }
        ),
        encoding="utf-8",
    )

    checksum = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()

    version = SimpleNamespace(
        id=uuid4(),
        modelo_id=uuid4(),
        version="0.1.0",
        ruta_artefacto=str(path),
        checksum=checksum,
        algoritmo="HISTORICAL_MEDIAN_RETURN",
        framework="ALPHAINVEST_NATIVE",
    )

    with pytest.raises(
        AIArtifactLoadError
    ):
        PriceForecastModelLoader.load(
            version
        )