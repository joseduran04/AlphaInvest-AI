from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrendXGBoostConfiguration:
    """Configuración congelada del clasificador de tendencia."""

    n_estimators: int
    max_depth: int
    learning_rate: float
    min_child_weight: float
    subsample: float
    colsample_bytree: float
    reg_alpha: float
    reg_lambda: float

    use_balanced_weights: bool
    random_state: int


PREDICTION_TREND_XGBOOST_V1 = TrendXGBoostConfiguration(
    n_estimators=100,
    max_depth=3,
    learning_rate=0.05,
    min_child_weight=2,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    use_balanced_weights=True,
    random_state=42,
)