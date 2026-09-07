def calculate_improvement(
    *,
    baseline: float,
    candidate: float,
) -> float:
    """Calcula la mejora porcentual frente a un baseline."""

    if baseline == 0:
        return 0.0

    return (
        (baseline - candidate)
        / baseline
    ) * 100.0