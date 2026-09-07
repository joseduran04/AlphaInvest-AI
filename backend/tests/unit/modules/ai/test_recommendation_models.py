from alphainvest.modules.ai.infrastructure.models import (
    AnalysisEvidenceModel,
    RecommendationAssetModel,
    RecommendationModel,
)


def test_recommendation_model_table() -> None:
    table = RecommendationModel.__table__

    assert table.schema == "ai"
    assert table.name == "recomendaciones"

    assert table.c.id.primary_key
    assert not table.c.solicitud_id.nullable
    assert not table.c.usuario_id.nullable
    assert table.c.perfil_riesgo_id.nullable
    assert table.c.portafolio_id.nullable
    assert not table.c.version_modelo_id.nullable

    assert not table.c.tipo.nullable
    assert not table.c.titulo.nullable
    assert not table.c.resumen.nullable
    assert not table.c.justificacion.nullable
    assert not table.c.nivel_riesgo.nullable
    assert not table.c.horizonte.nullable
    assert not table.c.confianza.nullable
    assert not table.c.advertencia.nullable

    assert table.c.fecha_expiracion.nullable
    assert table.c.fecha_aceptacion.nullable
    assert table.c.fecha_rechazo.nullable


def test_recommendation_asset_composite_primary_key() -> None:
    table = RecommendationAssetModel.__table__

    assert table.schema == "ai"
    assert table.name == "recomendacion_activos"

    primary_keys = {
        column.name
        for column in table.primary_key.columns
    }

    assert primary_keys == {
        "recomendacion_id",
        "activo_id",
    }

    assert not table.c.accion.nullable
    assert table.c.porcentaje_objetivo.nullable
    assert table.c.precio_referencia.nullable
    assert table.c.precio_objetivo.nullable
    assert table.c.limite_perdida.nullable
    assert table.c.confianza.nullable
    assert table.c.justificacion.nullable


def test_analysis_evidence_model_table() -> None:
    table = AnalysisEvidenceModel.__table__

    assert table.schema == "ai"
    assert table.name == "evidencias_analisis"

    assert table.c.id.primary_key
    assert not table.c.solicitud_id.nullable

    assert table.c.recomendacion_id.nullable
    assert table.c.prediccion_id.nullable

    assert not table.c.tipo_evidencia.nullable
    assert not table.c.entidad_origen.nullable
    assert not table.c.descripcion.nullable

    assert table.c.identificador_origen.nullable
    assert table.c.valor_numerico.nullable
    assert table.c.unidad.nullable
    assert table.c.peso.nullable
    assert table.c.contribucion.nullable
    assert table.c.datos.nullable
    assert table.c.fecha_evidencia.nullable