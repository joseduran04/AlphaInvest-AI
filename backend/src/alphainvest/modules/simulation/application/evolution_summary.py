from decimal import Decimal

from alphainvest.modules.simulation.domain.historical import (
    HistoricalPortfolioEvolution,
)

# Límite de puntos guardados en el resumen para graficar la evolución.
MAX_EVOLUTION_POINTS = 750


def build_evolution_summary(
    evolution: HistoricalPortfolioEvolution,
    *,
    max_points: int = MAX_EVOLUTION_POINTS,
) -> list[dict[str, str]]:
    """Serie diaria para graficar: valor del portafolio y capital aportado.

    ``aportado`` = capital inicial + aportaciones acumuladas hasta la fecha.
    Si hay más de ``max_points`` sesiones se muestrea de forma uniforme,
    conservando siempre la primera y la última.
    """

    points = evolution.points

    if not points:
        return []

    contributed = evolution.initial_capital
    series: list[dict[str, str]] = []

    for point in points:
        contributed += point.contribution_amount
        series.append(
            {
                "fecha": point.date.isoformat(),
                "valor": str(point.total_value),
                "aportado": str(contributed),
            }
        )

    if len(series) <= max_points or max_points < 2:
        return series

    step = Decimal(len(series) - 1) / Decimal(max_points - 1)
    indexes = sorted(
        {
            int((step * index).to_integral_value())
            for index in range(max_points)
        }
        | {0, len(series) - 1}
    )

    return [series[index] for index in indexes]
