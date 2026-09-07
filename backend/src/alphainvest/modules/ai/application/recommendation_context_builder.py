from datetime import timedelta
from uuid import UUID

from alphainvest.modules.ai.domain.analysis_enums import (
    AnalysisRequestStatus,
    AnalysisType,
)
from alphainvest.modules.ai.domain.recommendation_context import (
    RecommendationContext,
    RecommendationIndicatorSignal,
    RecommendationPortfolioSignal,
    RecommendationPositionSignal,
    RecommendationPredictionSignal,
    RecommendationRiskProfileSignal,
)
from alphainvest.modules.ai.infrastructure.models import (
    AnalysisRequestModel,
)
from alphainvest.modules.ai.infrastructure.repository import (
    AIRepository,
)
from alphainvest.modules.market.infrastructure.repository import (
    MarketRepository,
)
from alphainvest.modules.portfolio.infrastructure.repository import (
    PortfolioRepository,
)
from alphainvest.modules.profile.infrastructure.repository import (
    ProfileRepository,
)


class RecommendationContextBuilder:
    """Construye el contexto normalizado para recomendaciones."""

    INDICATOR_LOOKBACK_DAYS = 30

    def __init__(
        self,
        *,
        ai_repository: AIRepository,
        market_repository: MarketRepository,
        profile_repository: ProfileRepository,
        portfolio_repository: PortfolioRepository,
    ) -> None:
        self._ai_repository = ai_repository
        self._market_repository = market_repository
        self._profile_repository = profile_repository
        self._portfolio_repository = portfolio_repository

    async def build(
        self,
        *,
        request: AnalysisRequestModel,
    ) -> RecommendationContext:
        self._validate_recommendation_request(
            request
        )

        parameters = request.parametros

        if not isinstance(parameters, dict):
            raise ValueError(
                "La solicitud RECOMENDACION no contiene "
                "parámetros válidos"
            )

        asset_id = self._parse_uuid_parameter(
            parameters,
            "asset_id",
        )

        prediction_request_id = (
            self._parse_uuid_parameter(
                parameters,
                "prediction_request_id",
            )
        )

        prediction_request = (
            await self._ai_repository
            .get_analysis_request(
                prediction_request_id
            )
        )

        if prediction_request is None:
            raise ValueError(
                "La solicitud ACTIVO asociada "
                "no existe"
            )

        self._validate_prediction_request(
            recommendation_request=request,
            prediction_request=prediction_request,
        )

        prediction = (
            await self._ai_repository
            .get_asset_prediction_by_request(
                request_id=prediction_request_id
            )
        )

        if prediction is None:
            raise ValueError(
                "La solicitud ACTIVO asociada no "
                "tiene una predicción persistida"
            )

        if prediction.activo_id != asset_id:
            raise ValueError(
                "La predicción ACTIVO no pertenece "
                "al activo solicitado"
            )

        latest_price = (
            await self._market_repository
            .get_latest_asset_price(
                asset_id=asset_id
            )
        )

        indicator_start_date = (
            request.fecha_referencia
            - timedelta(
                days=self.INDICATOR_LOOKBACK_DAYS
            )
        )

        indicators = (
            await self._market_repository
            .list_financial_indicators_for_ai(
                asset_id=asset_id,
                start_date=indicator_start_date,
                end_date=request.fecha_referencia,
            )
        )

        current_profile = (
            await self._profile_repository
            .get_current_profile(
                request.usuario_id
            )
        )

        portfolio_signal = (
            await self._build_portfolio_signal(
                request=request,
                asset_id=asset_id,
            )
        )

        horizon = request.horizonte

        if horizon is None:
            raise ValueError(
                "La solicitud RECOMENDACION "
                "no contiene horizonte"
            )

        return RecommendationContext(
            request_id=request.id,
            user_id=request.usuario_id,
            asset_id=asset_id,
            model_version_id=(
                prediction.version_modelo_id
            ),
            horizon=horizon,
            prediction=(
                RecommendationPredictionSignal(
                    prediction_id=prediction.id,
                    asset_id=prediction.activo_id,
                    base_date=prediction.fecha_base,
                    target_date=(
                        prediction.fecha_objetivo
                    ),
                    horizon=prediction.horizonte,
                    base_price=prediction.precio_base,
                    predicted_price=(
                        prediction.precio_predicho
                    ),
                    expected_return_percentage=(
                        prediction
                        .rendimiento_esperado_porcentaje
                    ),
                    trend=prediction.tendencia,
                    confidence=prediction.confianza,
                    bullish_probability=(
                        prediction
                        .probabilidad_alcista
                    ),
                    neutral_probability=(
                        prediction
                        .probabilidad_neutral
                    ),
                    bearish_probability=(
                        prediction
                        .probabilidad_bajista
                    ),
                )
            ),
            latest_price=(
                latest_price.cierre
                if latest_price is not None
                else None
            ),
            indicators=tuple(
                RecommendationIndicatorSignal(
                    indicator_type=(
                        indicator.tipo_indicador
                    ),
                    period=indicator.periodo,
                    value=indicator.valor,
                    date=indicator.fecha,
                )
                for indicator in indicators
            ),
            risk_profile=(
                RecommendationRiskProfileSignal(
                    profile_id=current_profile.id,
                    classification=(
                        current_profile.clasificacion
                    ),
                    score=current_profile.puntuacion,
                    confidence=(
                        current_profile.confianza
                    ),
                )
                if current_profile is not None
                else None
            ),
            portfolio=portfolio_signal,
        )

    async def _build_portfolio_signal(
        self,
        *,
        request: AnalysisRequestModel,
        asset_id: UUID,
    ) -> RecommendationPortfolioSignal | None:
        portfolio_id = request.portafolio_id

        if portfolio_id is None:
            return None

        portfolio = (
            await self._portfolio_repository
            .get_by_id_for_user(
                portfolio_id=portfolio_id,
                user_id=request.usuario_id,
            )
        )

        if portfolio is None:
            raise ValueError(
                "El portafolio asociado con la "
                "solicitud no existe o no pertenece "
                "al usuario"
            )

        position = (
            await self._portfolio_repository
            .get_position_by_asset(
                portfolio_id=portfolio.id,
                asset_id=asset_id,
            )
        )

        position_signal = None

        if position is not None:
            position_signal = (
                RecommendationPositionSignal(
                    position_id=position.id,
                    quantity=position.cantidad,
                    average_purchase_price=(
                        position
                        .precio_promedio_compra
                    ),
                    total_cost=position.costo_total,
                    current_price=(
                        position.precio_actual
                    ),
                    current_value=(
                        position.valor_actual
                    ),
                    profit_loss=(
                        position.ganancia_perdida
                    ),
                    return_percentage=(
                        position
                        .rendimiento_porcentaje
                    ),
                    status=position.estado,
                )
            )

        return RecommendationPortfolioSignal(
            portfolio_id=portfolio.id,
            initial_capital=(
                portfolio.capital_inicial
            ),
            cash_balance=portfolio.saldo_efectivo,
            status=portfolio.estado,
            position=position_signal,
        )

    @staticmethod
    def _validate_recommendation_request(
        request: AnalysisRequestModel,
    ) -> None:
        if (
            request.tipo_analisis
            != AnalysisType.RECOMMENDATION.value
        ):
            raise ValueError(
                "La solicitud no corresponde "
                "a RECOMENDACION"
            )

        if (
            request.estado
            not in {
                AnalysisRequestStatus.PENDING.value,
                AnalysisRequestStatus.RUNNING.value,
            }
        ):
            raise ValueError(
                "La solicitud RECOMENDACION no está "
                "en un estado procesable"
            )

    @staticmethod
    def _validate_prediction_request(
        *,
        recommendation_request: AnalysisRequestModel,
        prediction_request: AnalysisRequestModel,
    ) -> None:
        if (
            prediction_request.tipo_analisis
            != AnalysisType.ASSET.value
        ):
            raise ValueError(
                "prediction_request_id no corresponde "
                "a una solicitud ACTIVO"
            )

        if (
            prediction_request.estado
            != AnalysisRequestStatus.COMPLETED.value
        ):
            raise ValueError(
                "La solicitud ACTIVO asociada "
                "todavía no está COMPLETADA"
            )

        if (
            prediction_request.usuario_id
            != recommendation_request.usuario_id
        ):
            raise ValueError(
                "La solicitud ACTIVO asociada no "
                "pertenece al mismo usuario"
            )

    @staticmethod
    def _parse_uuid_parameter(
        parameters: dict[str, object],
        key: str,
    ) -> UUID:
        raw_value = parameters.get(key)

        if not isinstance(raw_value, str):
            raise ValueError(
                f"El parámetro {key} es obligatorio"
            )

        try:
            return UUID(raw_value)
        except ValueError as error:
            raise ValueError(
                f"El parámetro {key} no contiene "
                "un UUID válido"
            ) from error