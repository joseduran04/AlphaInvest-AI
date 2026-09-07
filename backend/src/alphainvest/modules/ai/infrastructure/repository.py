from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from alphainvest.modules.ai.infrastructure.models import (
    AIModelModel,
    AnalysisEvidenceModel,
    AnalysisRequestModel,
    AssetPredictionModel,
    ModelVersionModel,
    RecommendationAssetModel,
    RecommendationModel,
    SentimentAnalysisModel,
)


class AIRepository:
    """Acceso a datos del catálogo de modelos de IA."""

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def list_models(
        self,
        *,
        search: str | None,
        model_type: str | None,
        status: str | None,
        limit: int,
        offset: int,
    ) -> tuple[list[AIModelModel], int]:
        filters = []

        if search:
            pattern = f"%{search.strip()}%"
            filters.append(
                or_(
                    AIModelModel.codigo.ilike(pattern),
                    AIModelModel.nombre.ilike(pattern),
                    AIModelModel.objetivo.ilike(pattern),
                )
            )

        if model_type:
            filters.append(
                AIModelModel.tipo
                == model_type.strip().upper()
            )

        if status:
            filters.append(
                AIModelModel.estado
                == status.strip().upper()
            )

        statement = (
            select(AIModelModel)
            .where(*filters)
            .order_by(
                AIModelModel.codigo.asc()
            )
            .limit(limit)
            .offset(offset)
        )

        count_statement = (
            select(func.count(AIModelModel.id))
            .where(*filters)
        )

        result = await self._session.execute(statement)
        count_result = await self._session.execute(
            count_statement
        )

        return (
            list(result.scalars().all()),
            int(count_result.scalar_one()),
        )

    async def get_model(
        self,
        model_id: UUID,
    ) -> AIModelModel | None:
        statement = (
            select(AIModelModel)
            .where(
                AIModelModel.id == model_id
            )
            .options(
                selectinload(AIModelModel.versiones)
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_model_by_code(
        self,
        code: str,
    ) -> AIModelModel | None:
        statement = (
            select(AIModelModel)
            .where(
                AIModelModel.codigo
                == code.strip().upper()
            )
            .options(
                selectinload(AIModelModel.versiones)
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_model_version(
        self,
        version_id: UUID,
    ) -> ModelVersionModel | None:
        statement = (
            select(ModelVersionModel)
            .where(
                ModelVersionModel.id == version_id
            )
            .options(
                selectinload(ModelVersionModel.modelo)
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_active_model_version(
        self,
        version_id: UUID,
    ) -> ModelVersionModel | None:
        statement = (
            select(ModelVersionModel)
            .where(
                ModelVersionModel.id == version_id,
                ModelVersionModel.activa.is_(True),
                ModelVersionModel.fecha_activacion.is_not(
                    None
                ),
            )
            .options(
                selectinload(ModelVersionModel.modelo)
            )
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_model_versions(
        self,
        *,
        model_id: UUID,
    ) -> list[ModelVersionModel]:
        statement = (
            select(ModelVersionModel)
            .where(
                ModelVersionModel.modelo_id == model_id
            )
            .options(
                selectinload(ModelVersionModel.modelo)
            )
            .order_by(
                ModelVersionModel.fecha_registro.desc(),
                ModelVersionModel.version.desc(),
            )
        )

        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def get_active_version_for_model(
        self,
        model_id: UUID,
    ) -> ModelVersionModel | None:
        statement = (
            select(ModelVersionModel)
            .where(
                ModelVersionModel.modelo_id == model_id,
                ModelVersionModel.activa.is_(True),
                ModelVersionModel.fecha_activacion.is_not(
                    None
                ),
            )
            .options(
                selectinload(ModelVersionModel.modelo)
            )
            .limit(1)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_active_version_by_model_code(
        self,
        code: str,
    ) -> ModelVersionModel | None:
        statement = (
            select(ModelVersionModel)
            .join(
                AIModelModel,
                AIModelModel.id
                == ModelVersionModel.modelo_id,
            )
            .where(
                AIModelModel.codigo
                == code.strip().upper(),
                AIModelModel.estado == "ACTIVO",
                ModelVersionModel.activa.is_(True),
                ModelVersionModel.fecha_activacion.is_not(
                    None
                ),
            )
            .options(
                selectinload(ModelVersionModel.modelo)
            )
            .limit(1)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def update_model_status(
        self,
        model: AIModelModel,
        *,
        status: str,
    ) -> AIModelModel:
        model.estado = status

        await self._session.flush()
        await self._session.refresh(model)

        return model

    async def create_model_version(
        self,
        *,
        model_id: UUID,
        version: str,
        artifact_path: str,
        checksum: str,
        algorithm: str,
        framework: str | None,
        hyperparameters: dict[str, object] | None,
        metrics: dict[str, object] | None,
        training_dataset: dict[str, object] | None,
        trained_at: object,
        created_by: UUID | None,
    ) -> ModelVersionModel:
        model_version = ModelVersionModel(
            modelo_id=model_id,
            version=version,
            ruta_artefacto=artifact_path,
            checksum=checksum,
            algoritmo=algorithm,
            framework=framework,
            hiperparametros=hyperparameters,
            metricas=metrics,
            conjunto_entrenamiento=training_dataset,
            fecha_entrenamiento=trained_at,
            activa=False,
            creada_por=created_by,
        )

        self._session.add(model_version)

        await self._session.flush()
        await self._session.refresh(model_version)

        return model_version

    async def activate_model_version(
        self,
        version: ModelVersionModel,
    ) -> ModelVersionModel:
        if version.activa:
            return version

        active_version = (
            await self.get_active_version_for_model(
                version.modelo_id
            )
        )

        now = datetime.now(UTC)

        if (
            active_version is not None
            and active_version.id != version.id
        ):
            active_version.activa = False
            active_version.fecha_desactivacion = now

            await self._session.flush()

        version.activa = True
        version.fecha_activacion = now
        version.fecha_desactivacion = None

        await self._session.flush()
        await self._session.refresh(version)

        return version

    async def deactivate_model_version(
        self,
        version: ModelVersionModel,
    ) -> ModelVersionModel:
        if not version.activa:
            return version

        version.activa = False
        version.fecha_desactivacion = datetime.now(UTC)

        await self._session.flush()
        await self._session.refresh(version)

        return version

    async def create_analysis_request(
        self,
        *,
        user_id: UUID,
        analysis_type: str,
        horizon: str | None,
        reference_date: date,
        parameters: dict[str, object] | None,
        portfolio_id: UUID | None = None,
        risk_profile_id: UUID | None = None,
        simulation_execution_id: UUID | None = None,
        process_identifier: str | None = None,
    ) -> AnalysisRequestModel:
        request = AnalysisRequestModel(
            usuario_id=user_id,
            portafolio_id=portfolio_id,
            perfil_riesgo_id=risk_profile_id,
            ejecucion_simulacion_id=(
                simulation_execution_id
            ),
            tipo_analisis=analysis_type,
            horizonte=horizon,
            fecha_referencia=reference_date,
            parametros=parameters,
            estado="PENDIENTE",
            identificador_proceso=(
                process_identifier
            ),
        )

        self._session.add(request)

        await self._session.flush()
        await self._session.refresh(request)

        return request

    async def list_pending_asset_analysis_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "ACTIVO",
                AnalysisRequestModel.estado
                == "PENDIENTE",
                AnalysisRequestModel.horizonte
                == "CORTO_PLAZO",
            )
            .order_by(
                AnalysisRequestModel.fecha_solicitud.asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_running_asset_analysis_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "ACTIVO",
                AnalysisRequestModel.estado
                == "EJECUTANDO",
                AnalysisRequestModel.horizonte
                == "CORTO_PLAZO",
            )
            .order_by(
                AnalysisRequestModel.fecha_inicio.asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_pending_sentiment_analysis_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "SENTIMIENTO",
                AnalysisRequestModel.estado
                == "PENDIENTE",
                AnalysisRequestModel.horizonte.is_(
                    None
                ),
            )
            .order_by(
                AnalysisRequestModel
                .fecha_solicitud
                .asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_running_sentiment_analysis_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "SENTIMIENTO",
                AnalysisRequestModel.estado
                == "EJECUTANDO",
                AnalysisRequestModel.horizonte.is_(
                    None
                ),
            )
            .order_by(
                AnalysisRequestModel
                .fecha_inicio
                .asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_pending_recommendation_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "RECOMENDACION",
                AnalysisRequestModel.estado
                == "PENDIENTE",
            )
            .order_by(
                AnalysisRequestModel
                .fecha_solicitud
                .asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_running_recommendation_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "RECOMENDACION",
                AnalysisRequestModel.estado
                == "EJECUTANDO",
            )
            .order_by(
                AnalysisRequestModel
                .fecha_inicio
                .asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_pending_integral_analysis_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "INTEGRAL",
                AnalysisRequestModel.estado
                == "PENDIENTE",
            )
            .order_by(
                AnalysisRequestModel
                .fecha_solicitud
                .asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def list_running_integral_analysis_requests(
        self,
        *,
        limit: int,
    ) -> list[AnalysisRequestModel]:
        statement = (
            select(AnalysisRequestModel)
            .where(
                AnalysisRequestModel.tipo_analisis
                == "INTEGRAL",
                AnalysisRequestModel.estado
                == "EJECUTANDO",
            )
            .order_by(
                AnalysisRequestModel
                .fecha_inicio
                .asc(),
                AnalysisRequestModel.id.asc(),
            )
            .limit(limit)
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def increment_analysis_request_attempt(
        self,
        request: AnalysisRequestModel,
    ) -> int:
        request.intentos_procesamiento += 1

        await self._session.flush()
        await self._session.refresh(request)

        return request.intentos_procesamiento

    async def reset_analysis_request_for_retry(
        self,
        request: AnalysisRequestModel,
    ) -> AnalysisRequestModel:
        request.estado = "PENDIENTE"

        request.porcentaje_progreso = Decimal("0")

        request.fecha_inicio = None
        request.fecha_fin = None

        request.mensaje_error = None

        request.identificador_proceso = None

        await self._session.flush()
        await self._session.refresh(request)

        return request

    async def get_analysis_request(
        self,
        request_id: UUID,
    ) -> AnalysisRequestModel | None:
        statement = select(
            AnalysisRequestModel
        ).where(
            AnalysisRequestModel.id == request_id
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def update_analysis_request_parameters(
        self,
        request: AnalysisRequestModel,
        *,
        parameters: dict[str, object],
    ) -> AnalysisRequestModel:
        request.parametros = parameters

        await self._session.flush()
        await self._session.refresh(request)

        return request

    async def update_analysis_request_status(
        self,
        request: AnalysisRequestModel,
        *,
        status: str,
        progress: Decimal | None = None,
        error_message: str | None = None,
    ) -> AnalysisRequestModel:
        request.estado = status

        if progress is not None:
            request.porcentaje_progreso = progress

        request.mensaje_error = error_message

        await self._session.flush()
        await self._session.refresh(request)

        return request

    async def get_analysis_request_for_user(
        self,
        *,
        request_id: UUID,
        user_id: UUID,
    ) -> AnalysisRequestModel | None:
        statement = select(
            AnalysisRequestModel
        ).where(
            AnalysisRequestModel.id == request_id,
            AnalysisRequestModel.usuario_id == user_id,
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def create_asset_prediction(
        self,
        *,
        request_id: UUID,
        asset_id: UUID,
        version_model_id: UUID,
        base_date: date,
        target_date: date,
        horizon: str,
        base_price: Decimal,
        predicted_price: Decimal,
        expected_return_percentage: Decimal | None,
        trend: str,
        confidence: Decimal,
        bullish_probability: Decimal | None,
        neutral_probability: Decimal | None,
        bearish_probability: Decimal | None,
        input_features: dict[str, object] | None,
        model_output: dict[str, object] | None,
    ) -> AssetPredictionModel:
        prediction = AssetPredictionModel(
            solicitud_id=request_id,
            activo_id=asset_id,
            version_modelo_id=version_model_id,
            fecha_base=base_date,
            fecha_objetivo=target_date,
            horizonte=horizon,
            precio_base=base_price,
            precio_predicho=predicted_price,
            precio_minimo_estimado=None,
            precio_maximo_estimado=None,
            rendimiento_esperado_porcentaje=(
                expected_return_percentage
            ),
            tendencia=trend,
            confianza=confidence,
            probabilidad_alcista=(
                bullish_probability
            ),
            probabilidad_neutral=(
                neutral_probability
            ),
            probabilidad_bajista=(
                bearish_probability
            ),
            caracteristicas_entrada=input_features,
            salida_modelo=model_output,
        )

        self._session.add(prediction)

        await self._session.flush()
        await self._session.refresh(prediction)

        return prediction

    async def get_asset_prediction_by_request(
        self,
        *,
        request_id: UUID,
    ) -> AssetPredictionModel | None:
        statement = select(
            AssetPredictionModel
        ).where(
            AssetPredictionModel.solicitud_id
            == request_id
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def create_sentiment_analysis(
        self,
        *,
        request_id: UUID,
        asset_id: UUID | None,
        news_reference_id: UUID | None,
        version_model_id: UUID,
        source_type: str,
        source_identifier: str | None,
        sentiment: str,
        score: Decimal,
        confidence: Decimal,
        positive_probability: Decimal | None,
        neutral_probability: Decimal | None,
        negative_probability: Decimal | None,
        relevance: Decimal | None,
        language: str | None,
        detected_entities: (
            dict[str, object]
            | list[object]
            | None
        ),
        summary: str | None,
        content_date: datetime | None,
    ) -> SentimentAnalysisModel:
        analysis = SentimentAnalysisModel(
            solicitud_id=request_id,
            activo_id=asset_id,
            noticia_referencia_id=news_reference_id,
            version_modelo_id=version_model_id,
            tipo_fuente=source_type,
            identificador_fuente=source_identifier,
            sentimiento=sentiment,
            puntuacion=score,
            confianza=confidence,
            probabilidad_positiva=positive_probability,
            probabilidad_neutral=neutral_probability,
            probabilidad_negativa=negative_probability,
            relevancia=relevance,
            idioma=language,
            entidades_detectadas=detected_entities,
            resumen=summary,
            fecha_contenido=content_date,
        )

        self._session.add(
            analysis
        )

        await self._session.flush()
        await self._session.refresh(
            analysis
        )

        return analysis

    async def get_sentiment_analysis_by_request(
        self,
        *,
        request_id: UUID,
    ) -> SentimentAnalysisModel | None:
        statement = select(
            SentimentAnalysisModel
        ).where(
            SentimentAnalysisModel.solicitud_id
            == request_id
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def get_sentiment_analysis_by_request_and_news(
        self,
        *,
        request_id: UUID,
        news_reference_id: UUID,
    ) -> SentimentAnalysisModel | None:
        statement = select(
            SentimentAnalysisModel
        ).where(
            SentimentAnalysisModel.solicitud_id
            == request_id,
            SentimentAnalysisModel.noticia_referencia_id
            == news_reference_id,
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def create_recommendation(
        self,
        *,
        request_id: UUID,
        user_id: UUID,
        risk_profile_id: UUID | None,
        portfolio_id: UUID | None,
        model_version_id: UUID,
        recommendation_type: str,
        title: str,
        summary: str,
        justification: str,
        risk_level: str,
        horizon: str,
        confidence: Decimal,
        priority: int,
        warning: str,
        parameters: dict[str, object] | None,
        expiration_date: datetime | None,
    ) -> RecommendationModel:
        recommendation = RecommendationModel(
            solicitud_id=request_id,
            usuario_id=user_id,
            perfil_riesgo_id=risk_profile_id,
            portafolio_id=portfolio_id,
            version_modelo_id=model_version_id,
            tipo=recommendation_type,
            titulo=title,
            resumen=summary,
            justificacion=justification,
            nivel_riesgo=risk_level,
            horizonte=horizon,
            confianza=confidence,
            prioridad=priority,
            estado="GENERADA",
            advertencia=warning,
            parametros=parameters,
            fecha_expiracion=expiration_date,
        )

        self._session.add(recommendation)

        await self._session.flush()
        await self._session.refresh(recommendation)

        return recommendation

    async def get_recommendation_by_request(
        self,
        *,
        request_id: UUID,
    ) -> RecommendationModel | None:
        statement = select(
            RecommendationModel
        ).where(
            RecommendationModel.solicitud_id
            == request_id
        )

        result = await self._session.execute(
            statement
        )

        return result.scalar_one_or_none()

    async def create_recommendation_asset(
        self,
        *,
        recommendation_id: UUID,
        asset_id: UUID,
        action: str,
        target_percentage: Decimal | None,
        reference_price: Decimal | None,
        target_price: Decimal | None,
        loss_limit: Decimal | None,
        confidence: Decimal | None,
        priority: int,
        justification: str | None,
    ) -> RecommendationAssetModel:
        recommendation_asset = RecommendationAssetModel(
            recomendacion_id=recommendation_id,
            activo_id=asset_id,
            accion=action,
            porcentaje_objetivo=target_percentage,
            precio_referencia=reference_price,
            precio_objetivo=target_price,
            limite_perdida=loss_limit,
            confianza=confidence,
            prioridad=priority,
            justificacion=justification,
        )

        self._session.add(
            recommendation_asset
        )

        await self._session.flush()
        await self._session.refresh(
            recommendation_asset
        )

        return recommendation_asset

    async def list_recommendation_assets(
        self,
        *,
        recommendation_id: UUID,
    ) -> list[RecommendationAssetModel]:
        statement = (
            select(RecommendationAssetModel)
            .where(
                RecommendationAssetModel
                .recomendacion_id
                == recommendation_id
            )
            .order_by(
                RecommendationAssetModel
                .prioridad.asc(),
                RecommendationAssetModel
                .activo_id.asc(),
            )
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def create_analysis_evidence(
        self,
        *,
        request_id: UUID,
        recommendation_id: UUID | None,
        prediction_id: UUID | None,
        evidence_type: str,
        source_entity: str,
        source_identifier: str | None,
        description: str,
        numeric_value: Decimal | None,
        unit: str | None,
        weight: Decimal | None,
        contribution: str | None,
        data: dict[str, object] | None,
        evidence_date: datetime | None,
    ) -> AnalysisEvidenceModel:
        evidence = AnalysisEvidenceModel(
            solicitud_id=request_id,
            recomendacion_id=recommendation_id,
            prediccion_id=prediction_id,
            tipo_evidencia=evidence_type,
            entidad_origen=source_entity,
            identificador_origen=source_identifier,
            descripcion=description,
            valor_numerico=numeric_value,
            unidad=unit,
            peso=weight,
            contribucion=contribution,
            datos=data,
            fecha_evidencia=evidence_date,
        )

        self._session.add(
            evidence
        )

        await self._session.flush()
        await self._session.refresh(
            evidence
        )

        return evidence

    async def list_analysis_evidence_for_recommendation(
        self,
        *,
        recommendation_id: UUID,
    ) -> list[AnalysisEvidenceModel]:
        statement = (
            select(AnalysisEvidenceModel)
            .where(
                AnalysisEvidenceModel.recomendacion_id
                == recommendation_id
            )
            .order_by(
                AnalysisEvidenceModel.fecha_registro.asc(),
                AnalysisEvidenceModel.id.asc(),
            )
        )

        result = await self._session.execute(
            statement
        )

        return list(
            result.scalars().all()
        )

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()