from uuid import UUID, uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from alphainvest.infrastructure.database.session import (
    AsyncSessionFactory,
)

pytestmark = [
    pytest.mark.integration,
    pytest.mark.asyncio(loop_scope="module"),
]


async def _get_required_parent_ids(
    session: AsyncSession,
) -> tuple[UUID, UUID, UUID]:
    user_result = await session.execute(
        text(
            """
            SELECT id
            FROM app_auth.usuarios
            ORDER BY fecha_creacion
            LIMIT 1
            """
        )
    )
    user_id = user_result.scalar_one_or_none()

    asset_result = await session.execute(
        text(
            """
            SELECT id
            FROM market.activos
            WHERE estado = 'ACTIVO'
            ORDER BY fecha_alta
            LIMIT 1
            """
        )
    )
    asset_id = asset_result.scalar_one_or_none()

    version_result = await session.execute(
        text(
            """
            SELECT id
            FROM ai.versiones_modelo
            ORDER BY fecha_registro
            LIMIT 1
            """
        )
    )
    model_version_id = (
        version_result.scalar_one_or_none()
    )

    if (
        user_id is None
        or asset_id is None
        or model_version_id is None
    ):
        pytest.skip(
            "La base de integración no contiene "
            "usuario, activo o versión de modelo."
        )

    return (
        user_id,
        asset_id,
        model_version_id,
    )


async def _create_analysis_request(
    session: AsyncSession,
    *,
    user_id: UUID,
    analysis_type: str,
    parameters: dict[str, object] | None = None,
) -> UUID:
    request_id = uuid4()

    await session.execute(
        text(
            """
            INSERT INTO ai.solicitudes_analisis
            (
                id,
                usuario_id,
                tipo_analisis,
                horizonte,
                fecha_referencia,
                parametros,
                estado
            )
            VALUES
            (
                :id,
                :user_id,
                :analysis_type,
                'CORTO_PLAZO',
                CURRENT_DATE,
                CAST(:parameters AS JSONB),
                'COMPLETADA'
            )
            """
        ),
        {
            "id": request_id,
            "user_id": user_id,
            "analysis_type": analysis_type,
            "parameters": (
                None
                if parameters is None
                else __import__("json").dumps(
                    parameters
                )
            ),
        },
    )

    return request_id


async def _create_asset_prediction(
    session: AsyncSession,
    *,
    request_id: UUID,
    asset_id: UUID,
    model_version_id: UUID,
) -> UUID:
    prediction_id = uuid4()

    await session.execute(
        text(
            """
            INSERT INTO ai.predicciones_activo
            (
                id,
                solicitud_id,
                activo_id,
                version_modelo_id,
                fecha_base,
                fecha_objetivo,
                horizonte,
                precio_base,
                precio_predicho,
                rendimiento_esperado_porcentaje,
                tendencia,
                confianza
            )
            VALUES
            (
                :id,
                :request_id,
                :asset_id,
                :model_version_id,
                CURRENT_DATE,
                CURRENT_DATE + 1,
                'CORTO_PLAZO',
                100.00000000,
                101.00000000,
                1.00000000,
                'ALCISTA',
                0.80000000
            )
            """
        ),
        {
            "id": prediction_id,
            "request_id": request_id,
            "asset_id": asset_id,
            "model_version_id": model_version_id,
        },
    )

    return prediction_id


async def _create_recommendation(
    session: AsyncSession,
    *,
    request_id: UUID,
    user_id: UUID,
    model_version_id: UUID,
) -> UUID:
    recommendation_id = uuid4()

    await session.execute(
        text(
            """
            INSERT INTO ai.recomendaciones
            (
                id,
                solicitud_id,
                usuario_id,
                version_modelo_id,
                tipo,
                titulo,
                resumen,
                justificacion,
                nivel_riesgo,
                horizonte,
                confianza,
                prioridad,
                estado,
                advertencia,
                parametros
            )
            VALUES
            (
                :id,
                :request_id,
                :user_id,
                :model_version_id,
                'OBSERVAR',
                'Prueba de integridad',
                'Recomendación temporal de integración.',
                'Valida la trazabilidad entre solicitudes.',
                'MEDIO',
                'CORTO_PLAZO',
                0.80000000,
                1,
                'GENERADA',
                'Prueba automatizada; no constituye asesoría financiera.',
                CAST(:parameters AS JSONB)
            )
            """
        ),
        {
            "id": recommendation_id,
            "request_id": request_id,
            "user_id": user_id,
            "model_version_id": model_version_id,
            "parameters": "{}",
        },
    )

    return recommendation_id


async def _insert_model_evidence(
    session: AsyncSession,
    *,
    request_id: UUID,
    recommendation_id: UUID | None,
    prediction_id: UUID,
) -> None:
    await session.execute(
        text(
            """
            INSERT INTO ai.evidencias_analisis
            (
                id,
                solicitud_id,
                recomendacion_id,
                prediccion_id,
                tipo_evidencia,
                entidad_origen,
                identificador_origen,
                descripcion,
                peso,
                contribucion,
                datos
            )
            VALUES
            (
                :id,
                :request_id,
                :recommendation_id,
                :prediction_id,
                'MODELO',
                'ai.predicciones_activo',
                :source_identifier,
                'Evidencia temporal de integración.',
                1.00000000,
                'POSITIVA',
                '{}'::JSONB
            )
            """
        ),
        {
            "id": uuid4(),
            "request_id": request_id,
            "recommendation_id": (
                recommendation_id
            ),
            "prediction_id": prediction_id,
            "source_identifier": str(
                prediction_id
            ),
        },
    )


async def _build_cross_request_scenario(
    session: AsyncSession,
) -> tuple[
    UUID,
    UUID,
    UUID,
    UUID,
    UUID,
]:
    (
        user_id,
        asset_id,
        model_version_id,
    ) = await _get_required_parent_ids(
        session
    )

    source_request_a = (
        await _create_analysis_request(
            session,
            user_id=user_id,
            analysis_type="ACTIVO",
        )
    )

    prediction_a = (
        await _create_asset_prediction(
            session,
            request_id=source_request_a,
            asset_id=asset_id,
            model_version_id=model_version_id,
        )
    )

    source_request_b = (
        await _create_analysis_request(
            session,
            user_id=user_id,
            analysis_type="ACTIVO",
        )
    )

    prediction_b = (
        await _create_asset_prediction(
            session,
            request_id=source_request_b,
            asset_id=asset_id,
            model_version_id=model_version_id,
        )
    )

    recommendation_request = (
        await _create_analysis_request(
            session,
            user_id=user_id,
            analysis_type="RECOMENDACION",
            parameters={
                "asset_id": str(asset_id),
                "prediction_request_id": str(
                    source_request_a
                ),
            },
        )
    )

    recommendation_id = (
        await _create_recommendation(
            session,
            request_id=(
                recommendation_request
            ),
            user_id=user_id,
            model_version_id=model_version_id,
        )
    )

    return (
        recommendation_request,
        source_request_a,
        prediction_a,
        prediction_b,
        recommendation_id,
    )


async def test_allows_declared_cross_request_prediction() -> None:
    async with AsyncSessionFactory() as session:
        transaction = await session.begin()

        try:
            (
                recommendation_request,
                _,
                prediction_a,
                _,
                recommendation_id,
            ) = await _build_cross_request_scenario(
                session
            )

            await _insert_model_evidence(
                session,
                request_id=(
                    recommendation_request
                ),
                recommendation_id=(
                    recommendation_id
                ),
                prediction_id=prediction_a,
            )

            await session.flush()

        finally:
            await transaction.rollback()


async def test_rejects_undeclared_cross_request_prediction() -> None:
    async with AsyncSessionFactory() as session:
        transaction = await session.begin()

        try:
            (
                recommendation_request,
                _,
                _,
                prediction_b,
                recommendation_id,
            ) = await _build_cross_request_scenario(
                session
            )

            with pytest.raises(
                IntegrityError
            ) as exc_info:
                async with session.begin_nested():
                    await _insert_model_evidence(
                        session,
                        request_id=(
                            recommendation_request
                        ),
                        recommendation_id=(
                            recommendation_id
                        ),
                        prediction_id=(
                            prediction_b
                        ),
                    )

                    await session.flush()

            assert (
                getattr(
                    exc_info.value.orig,
                    "sqlstate",
                    None,
                )
                == "23514"
            )

        finally:
            await transaction.rollback()


async def test_rejects_cross_request_prediction_without_recommendation() -> None:
    async with AsyncSessionFactory() as session:
        transaction = await session.begin()

        try:
            (
                recommendation_request,
                _,
                prediction_a,
                _,
                _,
            ) = await _build_cross_request_scenario(
                session
            )

            with pytest.raises(
                IntegrityError
            ) as exc_info:
                async with session.begin_nested():
                    await _insert_model_evidence(
                        session,
                        request_id=(
                            recommendation_request
                        ),
                        recommendation_id=None,
                        prediction_id=prediction_a,
                    )

                    await session.flush()

            assert (
                getattr(
                    exc_info.value.orig,
                    "sqlstate",
                    None,
                )
                == "23514"
            )

        finally:
            await transaction.rollback()