import numpy as np
from sklearn.linear_model import (
    HuberRegressor,
    Ridge,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from alphainvest.modules.ai.application.regression_evaluator import (
    RegressionEvaluator,
)
from alphainvest.modules.ai.domain.ml_dataset import (
    MLRegressionDataset,
)
from alphainvest.modules.ai.domain.price_forecast_regression_result import (
    PriceForecastRegressionResult,
)


class PriceForecastLinearService:
    """Baselines lineales para diagnóstico de regresión."""

    @staticmethod
    def build_ridge() -> Pipeline:
        return Pipeline(
            steps=[
                (
                    "scaler",
                    StandardScaler(),
                ),
                (
                    "regressor",
                    Ridge(
                        alpha=1.0,
                    ),
                ),
            ]
        )

    @staticmethod
    def build_huber() -> Pipeline:
        return Pipeline(
            steps=[
                (
                    "scaler",
                    StandardScaler(),
                ),
                (
                    "regressor",
                    HuberRegressor(
                        epsilon=1.35,
                        alpha=0.0001,
                        max_iter=1000,
                    ),
                ),
            ]
        )

    @classmethod
    def train_and_evaluate_ridge(
        cls,
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> tuple[
        Pipeline,
        PriceForecastRegressionResult,
    ]:
        return cls._train_and_evaluate(
            algorithm="RIDGE",
            pipeline=cls.build_ridge(),
            training=training,
            validation=validation,
        )

    @classmethod
    def train_and_evaluate_huber(
        cls,
        *,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> tuple[
        Pipeline,
        PriceForecastRegressionResult,
    ]:
        return cls._train_and_evaluate(
            algorithm="HUBER_REGRESSOR",
            pipeline=cls.build_huber(),
            training=training,
            validation=validation,
        )

    @classmethod
    def _train_and_evaluate(
        cls,
        *,
        algorithm: str,
        pipeline: Pipeline,
        training: MLRegressionDataset,
        validation: MLRegressionDataset,
    ) -> tuple[
        Pipeline,
        PriceForecastRegressionResult,
    ]:
        cls._validate_datasets(
            training=training,
            validation=validation,
        )

        pipeline.fit(
            training.features,
            training.targets,
        )

        prediction_values = pipeline.predict(
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

        result = PriceForecastRegressionResult(
            algorithm=algorithm,
            training_rows=training.rows,
            validation_rows=validation.rows,
            metrics=metrics,
        )

        return pipeline, result

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