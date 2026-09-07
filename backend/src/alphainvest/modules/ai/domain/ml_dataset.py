from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

FloatMatrix = NDArray[np.float64]
IntegerVector = NDArray[np.int64]
FloatVector = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class MLClassificationDataset:
    """Matrices numéricas para clasificación supervisada."""

    feature_names: tuple[str, ...]
    features: FloatMatrix
    targets: IntegerVector

    @property
    def rows(self) -> int:
        return int(self.features.shape[0])

    @property
    def columns(self) -> int:
        return int(self.features.shape[1])


@dataclass(frozen=True, slots=True)
class MLRegressionDataset:
    """Matrices numéricas para regresión supervisada."""

    feature_names: tuple[str, ...]
    features: FloatMatrix
    targets: FloatVector

    @property
    def rows(self) -> int:
        return int(self.features.shape[0])

    @property
    def columns(self) -> int:
        return int(self.features.shape[1])