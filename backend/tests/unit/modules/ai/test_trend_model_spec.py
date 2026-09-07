import pytest

from alphainvest.modules.ai.domain.trend_model_spec import (
    PREDICTION_TREND_XGBOOST_V1,
)

pytestmark = pytest.mark.unit


def test_prediction_trend_xgboost_v1_is_frozen() -> None:
    configuration = PREDICTION_TREND_XGBOOST_V1

    assert configuration.n_estimators == 100
    assert configuration.max_depth == 3
    assert configuration.learning_rate == 0.05
    assert configuration.min_child_weight == 2
    assert configuration.subsample == 0.8
    assert configuration.colsample_bytree == 0.8
    assert configuration.reg_alpha == 0.1
    assert configuration.reg_lambda == 1.0
    assert configuration.use_balanced_weights is True
    assert configuration.random_state == 42