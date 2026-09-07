from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SentimentClassificationResult:
    accuracy: float
    balanced_accuracy: float
    macro_f1: float

    labels: tuple[str, ...]

    confusion_matrix: tuple[
        tuple[int, ...],
        ...
    ]