import numpy as np
from xgboost import XGBRegressor

from alphainvest.modules.ai.application.regression_evaluator import (
    RegressionEvaluator,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLRegressionDataset,
)
from alphainvest.modules.ai.domain.price_forecast_xgboost_result import (
    PriceForecastXGBoostResult,
)


class PriceForecastXGBoostService:
    """Entrena XGBoost para rendimiento futuro."""

    ALGORITHM = "XGBOOST_REGRESSOR"

    @staticmethod
    def build_regressor() -> XGBRegressor:
        return XGBRegressor(
            objective="reg:squarederror",
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            min_child_weight=2,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            eval_metric="rmse",
            random_state=42,
            n_jobs=1,
            tree_method="hist",
        )

    @classmethod
    def train_and_evaluate(
        cls,
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> tuple[
        XGBRegressor,
        PriceForecastXGBoostResult,
    ]:
        cls._validate_datasets(
            training=training,
            validation=validation,
        )

        regressor = cls.build_regressor()

        regressor.fit(
            training.features,
            training.targets,
        )

        prediction_values = regressor.predict(
            validation.features
        )

        predictions = np.asarray(
            prediction_values,
            dtype=np.float64,
        )

        metrics = RegressionEvaluator.evaluate(
            expected=validation.targets,
            predicted=predictions,
        )

        result = PriceForecastXGBoostResult(
            algorithm=cls.ALGORITHM,
            training_rows=training.rows,
            validation_rows=validation.rows,
            metrics=metrics,
        )

        return regressor, result

    @staticmethod
    def _validate_datasets(
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> None:
        if training.rows == 0:
            raise ValueError(
                "El conjunto de entrenamiento está vacío"
            )

        if validation.rows == 0:
            raise ValueError(
                "El conjunto de validación está vacío"
            )

        if (
            training.feature_names
            != validation.feature_names
        ):
            raise ValueError(
                "Train y validation deben utilizar "
                "las mismas features"
            )